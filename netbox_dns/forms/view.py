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
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import View


__all__ = (
    "ViewForm",
    "ViewFilterForm",
    "ViewImportForm",
    "ViewBulkEditForm",
)


class ViewForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "default_view", "description", "tags", name="View"),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
    )

    class Meta:
        model = View
        fields = ("name", "default_view", "description", "tags", "tenant")


class ViewFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = View
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "default_view", "description", name="Attributes"),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    name = forms.CharField(
        required=False,
    )
    default_view = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )
    description = forms.CharField(
        required=False,
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
        fields = ("name", "description", "tenant", "tags")


class ViewBulkEditForm(NetBoxModelBulkEditForm):
    model = View

    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    fieldsets = (
        FieldSet(
            "name",
            "description",
            name="Attributes",
        ),
        FieldSet("tenant", name="Tenancy"),
    )

    nullable_fields = ("description", "tenant")
