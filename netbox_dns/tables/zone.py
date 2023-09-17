import django_tables2 as tables

from netbox.tables import (
    ChoiceFieldColumn,
    NetBoxTable,
    TagColumn,
    ActionsColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import Zone


class ZoneTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    view = tables.Column(
        linkify=True,
    )
    soa_mname = tables.Column(
        linkify=True,
    )
    status = ChoiceFieldColumn()
    tags = TagColumn(
        url_name="plugins:netbox_dns:zone_list",
    )
    default_ttl = tables.Column(
        verbose_name="Default TTL",
    )

    def render_name(self, value, record):
        return record.display_name

    class Meta(NetBoxTable.Meta):
        model = Zone
        fields = (
            "pk",
            "name",
            "view",
            "status",
            "description",
            "tags",
            "default_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial",
            "tenant",
            "tenant_group",
        )
        default_columns = (
            "pk",
            "name",
            "view",
            "status",
            "tags",
        )


class RelatedZoneTable(NetBoxTable):
    actions = ActionsColumn(actions=())

    name = tables.Column(
        linkify=True,
    )
    view = tables.Column(
        linkify=True,
    )
    arpa_network = tables.Column(
        verbose_name="Covered Prefix",
    )

    class Meta(NetBoxTable.Meta):
        model = Zone
        fields = (
            "name",
            "view",
            "arpa_network",
        )
        default_columns = (
            "name",
            "view",
            "arpa_network",
        )
