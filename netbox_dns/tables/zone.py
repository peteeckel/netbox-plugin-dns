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
    registrar = tables.Column(
        linkify=True,
    )
    registrant = tables.Column(
        linkify=True,
    )
    admin_c = tables.Column(
        linkify=True,
    )
    tech_c = tables.Column(
        linkify=True,
    )
    billing_c = tables.Column(
        linkify=True,
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
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
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
