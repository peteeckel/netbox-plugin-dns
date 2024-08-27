from django import forms

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
            name="RegistrationContact",
        ),
        FieldSet("tags", name="Tags"),
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
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "contact_id", "description", name="Attributes"),
        FieldSet(
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            name="Address",
        ),
        FieldSet("phone", "phone_ext", "fax", "fax_ext", "email", name="Communication"),
    )

    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    contact_id = forms.CharField(
        required=False,
        label="RegistrationContact ID",
    )
    organization = forms.CharField(
        required=False,
    )
    street = forms.CharField(
        required=False,
    )
    city = forms.CharField(
        required=False,
    )
    state_province = forms.CharField(
        required=False,
        label="State/Province",
    )
    postal_code = forms.CharField(
        required=False,
        label="Postal Code",
    )
    country = forms.CharField(
        required=False,
    )
    phone = forms.CharField(
        required=False,
    )
    phone_ext = forms.CharField(
        required=False,
        label="Phone Extension",
    )
    fax = forms.CharField(
        required=False,
    )
    fax_ext = forms.CharField(
        required=False,
        label="Fax Extension",
    )
    email = forms.CharField(
        required=False,
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

    name = forms.CharField(
        required=False,
        label="Name",
    )
    description = forms.CharField(
        required=False,
        label="Description",
    )
    organization = forms.CharField(
        required=False,
        label="Organization",
    )
    street = forms.CharField(
        required=False,
        label="Street",
    )
    city = forms.CharField(
        required=False,
        label="City",
    )
    state_province = forms.CharField(
        required=False,
        label="State/Province",
    )
    postal_code = forms.CharField(
        required=False,
        label="Postal Code",
    )
    country = forms.CharField(
        required=False,
        label="Country",
    )
    phone = forms.CharField(
        required=False,
        label="Phone",
    )
    phone_ext = forms.CharField(
        required=False,
        label="Phone Extension",
    )
    fax = forms.CharField(
        required=False,
        label="Fax",
    )
    fax_ext = forms.CharField(
        required=False,
        label="Fax Extension",
    )
    email = forms.CharField(
        required=False,
        label="Email Address",
    )

    fieldsets = (
        FieldSet("name", "description", name="Attributes"),
        FieldSet(
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            name="Address",
        ),
        FieldSet(
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            name="Communication",
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
