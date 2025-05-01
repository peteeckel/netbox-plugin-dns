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
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import NameServer, Zone
from netbox_dns.utilities import name_to_unicode


__all__ = (
    "NameServerForm",
    "NameServerFilterForm",
    "NameServerImportForm",
    "NameServerBulkEditForm",
)


class NameServerForm(TenancyForm, NetBoxModelForm):
    class Meta:
        model = NameServer

        fields = (
            "name",
            "description",
            "tags",
            "tenant_group",
            "tenant",
        )

    fieldsets = (
        FieldSet(
            "name",
            "description",
            name=_("Nameserver"),
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
        FieldSet(
            "tags",
            name=_("Tags"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    name = forms.CharField(
        required=True,
        label=_("Name"),
    )


class NameServerFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = NameServer

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "zone_id",
            "soa_zone_id",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name=_("Tenancy"),
        ),
    )

    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Zones"),
    )
    soa_zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("SOA Zones"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    tag = TagFilterField(NameServer)


class NameServerImportForm(NetBoxModelImportForm):
    class Meta:
        model = NameServer

        fields = (
            "name",
            "description",
            "tenant",
            "tags",
        )

    name = forms.CharField(
        label=_("Name"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )


class NameServerBulkEditForm(NetBoxModelBulkEditForm):
    model = NameServer

    fieldsets = (
        FieldSet(
            "description",
            "tenant_group",
            "tenant",
            "tags",
            name=_("Attributes"),
        ),
    )

    nullable_fields = (
        "description",
        "tenant",
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
