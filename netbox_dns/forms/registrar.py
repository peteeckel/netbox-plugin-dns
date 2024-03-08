from django import forms

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import TagFilterField

from netbox_dns.models import Registrar


class RegistrarForm(NetBoxModelForm):
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


class RegistrarFilterForm(NetBoxModelFilterSetForm):
    model = Registrar
    fieldsets = (
        (None, ("q", "filter_id", "tags")),
        (
            "Attributes",
            (
                "name",
                "iana_id",
                "description",
            ),
        ),
        (
            "Contact",
            ("address", "referral_url", "whois_server", "abuse_email", "abuse_phone"),
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
    tags = TagFilterField(Registrar)


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
    address = forms.CharField(
        required=False,
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
        (
            None,
            (
                "iana_id",
                "description",
                "address",
                "referral_url",
                "whois_server",
                "abuse_email",
                "abuse_phone",
            ),
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
