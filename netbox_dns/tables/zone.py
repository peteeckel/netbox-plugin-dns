import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import (
    ChoiceFieldColumn,
    NetBoxTable,
    TagColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import Zone


__all__ = ("ZoneTable",)


class ZoneTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    view = tables.Column(
        verbose_name=_("View"),
        linkify=True,
    )
    soa_mname = tables.Column(
        verbose_name=_("SOA MName"),
        linkify=True,
    )
    status = ChoiceFieldColumn(
        verbose_name=_("Status"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:zone_list",
    )
    default_ttl = tables.Column(
        verbose_name="Default TTL",
    )
    rfc2317_prefix = tables.Column(
        verbose_name=_("RFC2317 Prefix"),
    )
    rfc2317_parent_zone = tables.Column(
        verbose_name=_("RFC2317 Parent Zone"),
        linkify=True,
    )
    registrar = tables.Column(
        verbose_name=_("Registrar"),
        linkify=True,
    )
    registrant = tables.Column(
        verbose_name=_("Registrant"),
        linkify=True,
    )
    admin_c = tables.Column(
        verbose_name=_("Administrative Contact"),
        linkify=True,
    )
    tech_c = tables.Column(
        verbose_name=_("Technical Contact"),
        linkify=True,
    )
    billing_c = tables.Column(
        verbose_name=_("Billing Contact"),
        linkify=True,
    )

    def render_name(self, value, record):
        return record.display_name

    class Meta(NetBoxTable.Meta):
        model = Zone
        fields = (
            "description",
            "soa_rname",
            "soa_serial",
            "rfc2317_parent_managed",
            "registry_domain_id",
        )
        default_columns = (
            "name",
            "view",
            "status",
            "tags",
        )
