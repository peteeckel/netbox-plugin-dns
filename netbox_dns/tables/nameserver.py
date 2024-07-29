import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import NameServer


__all__ = ("NameServerTable",)


class NameServerTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:nameserver_list",
    )

    def render_name(self, value, record):
        return record.display_name

    class Meta(NetBoxTable.Meta):
        model = NameServer
        fields = (
            "name",
            "description",
            "tags",
            "tenant",
            "tenant_group",
        )
        default_columns = (
            "name",
            "tags",
        )
