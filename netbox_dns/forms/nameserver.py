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

from netbox_dns.models import NameServer
from netbox_dns.utilities import name_to_unicode


class NameServerForm(TenancyForm, NetBoxModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    fieldsets = (
        ("Nameserver", ("name", "description", "tags")),
        ("Tenancy", ("tenant_group", "tenant")),
    )

    class Meta:
        model = NameServer
        fields = ("name", "description", "tags", "tenant")


class NameServerFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = NameServer

    name = forms.CharField(
        required=False,
        label="Name",
    )
    tag = TagFilterField(NameServer)

    fieldsets = (
        (None, ("q", "filter_id", "tag")),
        ("Attributes", ("name",)),
        ("Tenant", ("tenant_group_id", "tenant_id")),
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
        )


class NameServerBulkEditForm(NetBoxModelBulkEditForm):
    model = NameServer

    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        nullable_fields = ("description", "tenant")
