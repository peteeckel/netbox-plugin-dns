import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import (
    ChoiceFieldColumn,
    NetBoxTable,
    TagColumn,
    ActionsColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import Zone


__all__ = (
    "ZoneTable",
    "ZoneDisplayTable",
)


class ZoneTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = Zone

        fields = (
            "description",
            "soa_rname",
            "soa_serial",
            "inline_signing",
            "rfc2317_parent_managed",
            "registry_domain_id",
            "expiration_date",
            "domain_status",
        )

        default_columns = (
            "name",
            "view",
            "status",
            "tags",
        )

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
        verbose_name=_("Default TTL"),
    )
    dnssec_policy = tables.Column(
        verbose_name=_("DNSSEC Policy"),
        linkify=True,
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
    domain_status = ChoiceFieldColumn(
        verbose_name=_("Domain Status"),
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


class ZoneDisplayTable(ZoneTable):
    class Meta(ZoneTable.Meta):
        pass

    actions = ActionsColumn(actions=("changelog",))
