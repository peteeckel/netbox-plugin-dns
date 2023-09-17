from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    TagFilterField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
)
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import View


class ViewForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        ("View", ("name", "description", "tags")),
        ("Tenancy", ("tenant_group", "tenant")),
    )

    class Meta:
        model = View
        fields = ("name", "description", "tags", "tenant")


class ViewFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = View
    fieldsets = (
        (None, ("q", "filter_id", "tag")),
        ("Attributes", ("name",)),
        ("Tenant", ("tenant_group_id", "tenant_id")),
    )

    name = forms.CharField(
        required=False,
        label="Name",
    )
    tag = TagFilterField(View)


class ViewImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Assigned tenant",
    )

    class Meta:
        model = View
        fields = ("name", "description", "tenant")


class ViewBulkEditForm(NetBoxModelBulkEditForm):
    model = View

    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        nullable_fields = ("description", "tenant")
