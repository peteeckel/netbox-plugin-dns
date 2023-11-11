import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn

from netbox_dns.models import Registrar


class RegistrarTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:registrar_list",
    )

    class Meta(NetBoxTable.Meta):
        model = Registrar
        fields = (
            "name",
            "iana_id",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "tags",
        )
        default_columns = ("name", "iana_id", "referral_url")
