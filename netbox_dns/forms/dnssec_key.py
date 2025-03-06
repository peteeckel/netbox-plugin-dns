from django import forms
from django.utils.translation import gettext_lazy as _

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
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import DNSSECKey


__all__ = (
    "DNSSECKeyForm",
    "DNSSECKeyFilterForm",
    "DNSSECKeyImportForm",
    "DNSSECKeyBulkEditForm",
)


class DNSSECKeyForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "description", name=_("Attributes")),
        FieldSet("type", "lifetime", "algorithm", "key_size", name=_("Key Properties")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    class Meta:
        model = DNSSECKey
        fields = (
            "name",
            "description",
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            "tenant_group",
            "tenant",
            "tags",
        )


class DNSSECKeyFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = DNSSECKey
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "description", name=_("Attributes")),
        FieldSet("type", "lifetime", "algorithm", "key_size", name=_("Key Properties")),
        FieldSet("type", "tenant_id", name=_("Tenancy")),
    )

    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    tag = TagFilterField(DNSSECKey)


class DNSSECKeyImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )

    class Meta:
        model = DNSSECKey
        fields = ("name", "description", "type", "lifetime", "algorithm", "key_size", "tenant", "tags")


class DNSSECKeyBulkEditForm(NetBoxModelBulkEditForm):
    model = DNSSECKey

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
            "description",
            name=_("Attributes"),
        ),
        FieldSet("type", "lifetime", "algorithm", "key_size", name=_("Key Properties")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
    )

    nullable_fields = ("description", "tenant", "lifetime", "key_size")
