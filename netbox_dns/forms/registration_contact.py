from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import TagFilterField
from utilities.forms.rendering import FieldSet

from netbox_dns.models import RegistrationContact


__all__ = (
    "RegistrationContactForm",
    "RegistrationContactFilterForm",
    "RegistrationContactImportForm",
    "RegistrationContactBulkEditForm",
)


class RegistrationContactForm(NetBoxModelForm):
    fieldsets = (
        FieldSet(
            "name",
            "description",
            "contact_id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            name=_("Contact"),
        ),
        FieldSet(
            "tags",
            name="Tags",
        ),
    )

    class Meta:
        model = RegistrationContact

        fields = (
            "name",
            "description",
            "contact_id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            "tags",
        )


class RegistrationContactFilterForm(NetBoxModelFilterSetForm):
    model = RegistrationContact

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "contact_id",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            name=_("Address"),
        ),
        FieldSet(
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            name=_("Communication"),
        ),
    )

    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    contact_id = forms.CharField(
        required=False,
        label=_("Contact ID"),
    )
    organization = forms.CharField(
        required=False,
        label=_("Organization"),
    )
    street = forms.CharField(
        required=False,
        label=_("Street"),
    )
    city = forms.CharField(
        required=False,
        label=_("City"),
    )
    state_province = forms.CharField(
        required=False,
        label=_("State/Province"),
    )
    postal_code = forms.CharField(
        required=False,
        label=_("Postal Code"),
    )
    country = forms.CharField(
        required=False,
        label=_("Country"),
    )
    phone = forms.CharField(
        required=False,
        label=_("Phone"),
    )
    phone_ext = forms.CharField(
        required=False,
        label=_("Phone Extension"),
    )
    fax = forms.CharField(
        required=False,
        label=_("Fax"),
    )
    fax_ext = forms.CharField(
        required=False,
        label=_("Fax Extension"),
    )
    email = forms.CharField(
        required=False,
        label=_("Email Address"),
    )
    tag = TagFilterField(RegistrationContact)


class RegistrationContactImportForm(NetBoxModelImportForm):
    class Meta:
        model = RegistrationContact

        fields = (
            "name",
            "description",
            "contact_id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            "tags",
        )


class RegistrationContactBulkEditForm(NetBoxModelBulkEditForm):
    model = RegistrationContact

    fieldsets = (
        FieldSet(
            "name",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            name=_("Address"),
        ),
        FieldSet(
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            name=_("Communication"),
        ),
    )

    nullable_fields = (
        "name",
        "description",
        "organization",
        "street",
        "city",
        "state_province",
        "postal_code",
        "country",
        "phone",
        "phone_ext",
        "fax",
        "fax_ext",
        "email",
    )

    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    organization = forms.CharField(
        required=False,
        label=_("Organization"),
    )
    street = forms.CharField(
        required=False,
        label=_("Street"),
    )
    city = forms.CharField(
        required=False,
        label=_("City"),
    )
    state_province = forms.CharField(
        required=False,
        label=_("State/Province"),
    )
    postal_code = forms.CharField(
        required=False,
        label=_("Postal Code"),
    )
    country = forms.CharField(
        required=False,
        label=_("Country"),
    )
    phone = forms.CharField(
        required=False,
        label=_("Phone"),
    )
    phone_ext = forms.CharField(
        required=False,
        label=_("Phone Extension"),
    )
    fax = forms.CharField(
        required=False,
        label=_("Fax"),
    )
    fax_ext = forms.CharField(
        required=False,
        label=_("Fax Extension"),
    )
    email = forms.CharField(
        required=False,
        label=_("Email Address"),
    )
