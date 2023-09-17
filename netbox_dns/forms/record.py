from django import forms
from django.urls import reverse_lazy

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    TagFilterField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect, APISelect
from utilities.forms import add_blank_choice
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import View, Zone, Record, RecordTypeChoices, RecordStatusChoices
from netbox_dns.utilities import name_to_unicode


class RecordForm(TenancyForm, NetBoxModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    disable_ptr = forms.BooleanField(
        label="Disable PTR",
        required=False,
    )
    ttl = forms.IntegerField(
        required=False,
        label="TTL",
    )

    fieldsets = (
        (
            "Record",
            (
                "name",
                "zone",
                "type",
                "value",
                "status",
                "ttl",
                "disable_ptr",
                "description",
                "tags",
            ),
        ),
        ("Tenancy", ("tenant_group", "tenant")),
    )

    class Meta:
        model = Record

        fields = (
            "name",
            "zone",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            "tags",
            "tenant",
        )


class RecordFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Record
    fieldsets = (
        (None, ("q", "filter_id", "tag")),
        ("Attributes", ("view_id", "zone_id", "name", "value", "status")),
        ("Tenant", ("tenant_group_id", "tenant_id")),
    )

    type = forms.MultipleChoiceField(
        choices=add_blank_choice(RecordTypeChoices),
        required=False,
    )
    name = forms.CharField(
        required=False,
        label="Name",
    )
    value = forms.CharField(
        required=False,
        label="Value",
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RecordStatusChoices),
        required=False,
    )
    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="Zone",
    )
    view_id = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        label="View",
    )
    tag = TagFilterField(Record)


class RecordImportForm(NetBoxModelImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        view = None
        if self.is_bound and "view" in self.data:
            try:
                view = self.fields["view"].to_python(self.data["view"])
            except forms.ValidationError:
                pass

        if view:
            self.fields["zone"].queryset = Zone.objects.filter(view=view)
        else:
            self.fields["zone"].queryset = Zone.objects.filter(view__isnull=True)

    zone = CSVModelChoiceField(
        queryset=Zone.objects.all(),
        to_field_name="name",
        required=True,
        help_text="Zone",
    )
    view = CSVModelChoiceField(
        queryset=View.objects.all(),
        to_field_name="name",
        required=False,
        help_text="View the zone belongs to",
    )
    type = CSVChoiceField(
        choices=RecordTypeChoices,
        required=True,
        help_text="Record Type",
    )
    status = CSVChoiceField(
        choices=RecordStatusChoices,
        required=False,
        help_text="Record status",
    )
    ttl = forms.IntegerField(
        required=False,
        help_text="TTL",
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label="Disable PTR",
        help_text="Disable generation of a PTR record",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Assigned tenant",
    )

    def is_valid(self):
        try:
            is_valid = super().is_valid()
        except Record.zone.RelatedObjectDoesNotExist:
            is_valid = False

        return is_valid

    class Meta:
        model = Record

        fields = (
            "zone",
            "view",
            "type",
            "name",
            "value",
            "ttl",
            "disable_ptr",
            "description",
            "tenant",
        )


class RecordBulkEditForm(NetBoxModelBulkEditForm):
    model = Record

    zone = DynamicModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:zone-list")}
        ),
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(RecordTypeChoices),
        required=False,
    )
    value = forms.CharField(
        required=False,
        label="Value",
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RecordStatusChoices),
        required=False,
    )
    ttl = forms.IntegerField(
        required=False,
        label="TTL",
    )
    disable_ptr = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label="Disable PTR"
    )
    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    fieldsets = (
        (
            None,
            (
                "zone",
                "type",
                "value",
                "status",
                "ttl",
                "disable_ptr",
                "description",
                "tenant",
            ),
        ),
    )
    nullable_fields = ("description", "ttl", "tenant")
