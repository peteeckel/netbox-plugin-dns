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
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    fieldsets = (
        FieldSet("name", "description", name="Nameserver"),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = NameServer
        fields = ("name", "description", "tags", "tenant")


class NameServerFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = NameServer

    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="Zones",
    )
    soa_zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="SOA Zones",
    )
    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    tag = TagFilterField(NameServer)

    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "zone_id", "soa_zone_id", "description", name="Attributes"),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )


class NameServerImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Assigned tenant",
    )

    class Meta:
        model = NameServer

        fields = (
            "name",
            "description",
            "tenant",
            "tags",
        )


class NameServerBulkEditForm(NetBoxModelBulkEditForm):
    model = NameServer

    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "tenant",
            "tags",
            name="Attributes",
        ),
    )

    nullable_fields = ("description", "tenant")
