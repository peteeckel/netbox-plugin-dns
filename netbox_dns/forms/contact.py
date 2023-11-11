from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import TagFilterField

from netbox_dns.models import Contact


class ContactForm(NetBoxModelForm):
    class Meta:
        model = Contact
        fields = (
            "name",
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


class ContactFilterForm(NetBoxModelFilterSetForm):
    model = Contact
    fieldsets = (
        (None, ("q", "name", "tags", "contact_id")),
        (
            "Address",
            (
                "organization",
                "street",
                "city",
                "state_province",
                "postal_code",
                "country",
            ),
        ),
        ("Communication", ("phone", "phone_ext", "fax", "fax_ext", "email")),
    )

    name = forms.CharField(
        required=False,
    )
    contact_id = forms.CharField(
        required=False,
        label="Contact ID",
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
    tags = TagFilterField(Contact)


class ContactImportForm(NetBoxModelImportForm):
    class Meta:
        model = Contact
        fields = (
            "name",
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


class ContactBulkEditForm(NetBoxModelBulkEditForm):
    model = Contact

    name = forms.CharField(
        required=False,
        label="Name",
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
        (None, ("name",)),
        (
            "Address",
            (
                "organization",
                "street",
                "city",
                "state_province",
                "postal_code",
                "country",
            ),
        ),
        (
            "Communication",
            (
                "phone",
                "phone_ext",
                "fax",
                "fax_ext",
                "email",
            ),
        ),
    )

    nullable_fields = (
        "name",
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
