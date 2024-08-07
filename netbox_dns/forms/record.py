from django import forms

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
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import View, Zone, Record
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices
from netbox_dns.utilities import name_to_unicode


__all__ = (
    "RecordForm",
    "RecordFilterForm",
    "RecordImportForm",
    "RecordBulkEditForm",
)


class RecordForm(TenancyForm, NetBoxModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_zone_id = self.initial.get("zone")
        if initial_zone_id is not None:
            self.initial["view"] = Zone.objects.get(pk=initial_zone_id).view
        else:
            self.initial["view"] = View.get_default_view()

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    view = DynamicModelChoiceField(
        queryset=View.objects.all(),
        required=False,
        label="View",
    )
    zone = DynamicModelChoiceField(
        queryset=Zone.objects.all(),
        required=True,
        query_params={
            "view_id": "$view",
        },
        label="Zone",
    )

    disable_ptr = forms.BooleanField(
        label="Disable PTR",
        required=False,
    )
    ttl = forms.IntegerField(
        required=False,
        label="TTL",
    )

    fieldsets = (
        FieldSet(
            "name",
            "view",
            "zone",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name="Record",
        ),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
        FieldSet("tags", name="Tags"),
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
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "zone_id",
            "name",
            "fqdn",
            "type",
            "value",
            "disable_ptr",
            "status",
            "description",
            name="Attributes",
        ),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    type = forms.MultipleChoiceField(
        choices=RecordTypeChoices,
        required=False,
    )
    name = forms.CharField(
        required=False,
    )
    fqdn = forms.CharField(
        required=False,
        label="FQDN",
    )
    value = forms.CharField(
        required=False,
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        label="Disable PTR",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )
    status = forms.MultipleChoiceField(
        choices=RecordStatusChoices,
        required=False,
    )
    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="Zone",
    )
    description = forms.CharField(
        required=False,
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

        if view is not None:
            self.fields["zone"].queryset = Zone.objects.filter(view=view)
        else:
            self.fields["zone"].queryset = Zone.objects.filter(
                view=View.get_default_view()
            )

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
            "tags",
        )


class RecordBulkEditForm(NetBoxModelBulkEditForm):
    model = Record

    zone = DynamicModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
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
        required=False,
        label="Disable PTR",
        widget=BulkEditNullBooleanSelect(),
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )

    fieldsets = (
        FieldSet(
            "zone",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name="Attributes",
        ),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
    )
    nullable_fields = ("description", "ttl", "tenant")
