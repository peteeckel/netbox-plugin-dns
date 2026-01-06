from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    PrimaryModelBulkEditForm,
    PrimaryModelFilterSetForm,
    PrimaryModelImportForm,
    PrimaryModelForm,
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


class RegistrarForm(PrimaryModelForm):
    class Meta:
        model = Registrar

        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "iana_id",
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
            "description",
            "iana_id",
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


class RegistrarFilterForm(PrimaryModelFilterSetForm):
    model = Registrar

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
            "owner_id",
        ),
        FieldSet(
            "name",
            "description",
            "iana_id",
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
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    address = forms.CharField(
        required=False,
        label=_("Address"),
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
    tag = TagFilterField(model)


class RegistrarImportForm(PrimaryModelImportForm):
    class Meta:
        model = Registrar

        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "iana_id",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "tags",
        )


class RegistrarBulkEditForm(PrimaryModelBulkEditForm):
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
