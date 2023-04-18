from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)

from utilities.forms.fields import TagFilterField

from netbox_dns.models import NameServer
from netbox_dns.utilities import name_to_unicode


class NameServerForm(NetBoxModelForm):
    """Form for creating a new NameServer object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

    class Meta:
        model = NameServer
        fields = ("name", "description", "tags")


class NameServerFilterForm(NetBoxModelFilterSetForm):
    """Form for filtering NameServer instances."""

    model = NameServer

    name = forms.CharField(
        required=False,
        label="Name",
    )
    tag = TagFilterField(NameServer)


class NameServerImportForm(NetBoxModelImportForm):
    class Meta:
        model = NameServer

        fields = ("name", "description")


class NameServerBulkEditForm(NetBoxModelBulkEditForm):
    model = NameServer

    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = ("description",)
