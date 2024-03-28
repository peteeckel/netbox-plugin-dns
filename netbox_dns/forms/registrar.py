from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import TagFilterField
from utilities.forms.rendering import FieldSet

from netbox_dns.models import Registrar


class RegistrarForm(NetBoxModelForm):
    class Meta:
        model = Registrar
        fieldsets = (
            FieldSet(
                "name",
                "iana_id",
                "description",
                "address",
                "referral_url",
                "whois_server",
                "abuse_email",
                "abuse_phone",
                name="Registrar",
            ),
            FieldSet("tags", name="Tags"),
        )
        fields = (
            "name",
            "iana_id",
            "description",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "tags",
        )


class RegistrarFilterForm(NetBoxModelFilterSetForm):
    model = Registrar
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "iana_id", "description", name="Attributes"),
        FieldSet(
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            name="Contact",
        ),
    )

    name = forms.CharField(
        required=False,
    )
    address = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    iana_id = forms.IntegerField(
        required=False,
        label="IANA ID",
    )
    referral_url = forms.CharField(
        required=False,
        label="Referral URL",
    )
    whois_server = forms.CharField(
        required=False,
        label="WHOIS Server",
    )
    abuse_email = forms.CharField(
        required=False,
        label="Abuse Email",
    )
    abuse_phone = forms.CharField(
        required=False,
        label="Abuse Phone",
    )
    tag = TagFilterField(Registrar)


class RegistrarImportForm(NetBoxModelImportForm):
    class Meta:
        model = Registrar
        fields = (
            "name",
            "iana_id",
            "description",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "tags",
        )


class RegistrarBulkEditForm(NetBoxModelBulkEditForm):
    model = Registrar

    iana_id = forms.IntegerField(
        required=False,
        label="IANA ID",
    )
    description = forms.CharField(
        required=False,
        label="Description",
    )
    address = forms.CharField(
        required=False,
        label="Address",
    )
    referral_url = forms.CharField(
        required=False,
        label="Referral URL",
    )
    whois_server = forms.CharField(
        required=False,
        label="WHOIS Server",
    )
    abuse_email = forms.CharField(
        required=False,
        label="Abuse Email",
    )
    abuse_phone = forms.CharField(
        required=False,
        label="Abuse Phone",
    )

    fieldsets = (
        FieldSet(
            "iana_id",
            "description",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            name="Attributes",
        ),
    )

    nullable_fields = (
        "iana_id",
        "description",
        "address",
        "referral_url",
        "whois_server",
        "abuse_email",
        "abuse_phone",
    )
