from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import TagFilterField

from netbox_dns.models import View


class ViewForm(NetBoxModelForm):
    """Form for creating a new View object."""

    class Meta:
        model = View
        fields = ("name", "description", "tags")


class ViewFilterForm(NetBoxModelFilterSetForm):
    """Form for filtering View instances."""

    name = forms.CharField(
        required=False,
        label="Name",
    )
    tag = TagFilterField(View)

    model = View


class ViewImportForm(NetBoxModelImportForm):
    class Meta:
        model = View
        fields = ("name", "description")


class ViewBulkEditForm(NetBoxModelBulkEditForm):
    model = View

    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = ["description"]
