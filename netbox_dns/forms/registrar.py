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

from netbox_dns.models import Registrar


__all__ = (
    "RegistrarForm",
    "RegistrarFilterForm",
    "RegistrarImportForm",
    "RegistrarBulkEditForm",
)


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
            name=_("Registrar"),
        ),
        FieldSet(
            "tags",
            name=_("Tags"),
        ),
    )


class RegistrarFilterForm(NetBoxModelFilterSetForm):
    model = Registrar

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "iana_id",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            name=_("Contact"),
        ),
    )

    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    address = forms.CharField(
        required=False,
        label=_("Address"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    iana_id = forms.IntegerField(
        required=False,
        label=_("IANA ID"),
    )
    referral_url = forms.CharField(
        required=False,
        label=_("Referral URL"),
    )
    whois_server = forms.CharField(
        required=False,
        label=_("WHOIS Server"),
    )
    abuse_email = forms.CharField(
        required=False,
        label=_("Abuse Email"),
    )
    abuse_phone = forms.CharField(
        required=False,
        label=_("Abuse Phone"),
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

    fieldsets = (
        FieldSet(
            "iana_id",
            "description",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            name=_("Attributes"),
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

    iana_id = forms.IntegerField(
        required=False,
        label=_("IANA ID"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    address = forms.CharField(
        required=False,
        label=_("Address"),
    )
    referral_url = forms.CharField(
        required=False,
        label=_("Referral URL"),
    )
    whois_server = forms.CharField(
        required=False,
        label=_("WHOIS Server"),
    )
    abuse_email = forms.CharField(
        required=False,
        label=_("Abuse Email"),
    )
    abuse_phone = forms.CharField(
        required=False,
        label=_("Abuse Phone"),
    )
