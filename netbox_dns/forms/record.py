from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as _p

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
from tenancy.models import Tenant, TenantGroup
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

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    view = DynamicModelChoiceField(
        queryset=View.objects.all(),
        required=False,
        initial_params={
            "zone": "$zone",
        },
        label=_p("DNS", "View"),
    )
    zone = DynamicModelChoiceField(
        queryset=Zone.objects.all(),
        required=True,
        query_params={
            "view_id": "$view",
        },
        label=_("Zone"),
    )

    disable_ptr = forms.BooleanField(
        required=False,
        label=_("Disable PTR"),
    )
    ttl = forms.IntegerField(
        required=False,
        label=_("TTL"),
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
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
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
            "tenant_group",
            "tenant",
            "tags",
        )


class RecordFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Record
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "view_id",
            "zone_id",
            "name",
            "fqdn",
            "type",
            "value",
            "disable_ptr",
            "status",
            "active",
            "description",
            name=_("Attributes"),
        ),
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
    )

    type = forms.MultipleChoiceField(
        choices=RecordTypeChoices,
        required=False,
        label=_("Type"),
    )
    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    fqdn = forms.CharField(
        required=False,
        label=_("FQDN"),
    )
    value = forms.CharField(
        required=False,
        label=_("Value"),
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Disable PTR"),
    )
    status = forms.MultipleChoiceField(
        choices=RecordStatusChoices,
        required=False,
        label=_("Status"),
    )
    view_id = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        label=_("View"),
    )
    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label=_("Zone"),
        query_params={
            "view_id": "$view_id",
        },
    )
    active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Active"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
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
        label=_("Zone"),
    )
    view = CSVModelChoiceField(
        queryset=View.objects.all(),
        to_field_name="name",
        required=False,
        label=_p("DNS", "View"),
    )
    type = CSVChoiceField(
        choices=RecordTypeChoices,
        required=True,
        label=_("Type"),
    )
    status = CSVChoiceField(
        choices=RecordStatusChoices,
        required=False,
        label=_("Status"),
    )
    ttl = forms.IntegerField(
        required=False,
        label=_("TTL"),
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label=_("Disable PTR"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
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
        label=_("Zone"),
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(RecordTypeChoices),
        required=False,
        label=_("Type"),
    )
    value = forms.CharField(
        required=False,
        label=_("Value"),
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RecordStatusChoices),
        required=False,
        label=_("Status"),
    )
    ttl = forms.IntegerField(
        required=False,
        label=_("TTL"),
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Disable PTR"),
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label=_("Description"),
    )
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
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
            name=_("Attributes"),
        ),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
    )
    nullable_fields = ("description", "ttl", "tenant")
