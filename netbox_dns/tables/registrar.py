import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, TagColumn

from netbox_dns.models import Registrar


__all__ = ("RegistrarTable",)


class RegistrarTable(NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = Registrar

        fields = (
            "description",
            "iana_id",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
        )

        default_columns = (
            "name",
            "iana_id",
            "referral_url",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:registrar_list",
    )
