import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import ZoneTemplate


__all__ = (
    "ZoneTemplateTable",
    "ZoneTemplateDisplayTable",
)


class ZoneTemplateTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:zonetemplate_list",
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

    class Meta(NetBoxTable.Meta):
        model = ZoneTemplate
        fields = (
            "name",
            "description",
            "tags",
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant",
            "tenant_group",
        )
        default_columns = (
            "name",
            "tags",
        )


class ZoneTemplateDisplayTable(ZoneTemplateTable):
    actions = ActionsColumn(actions="")

    class Meta(NetBoxTable.Meta):
        model = ZoneTemplate
        fields = (
            "name",
            "description",
        )
        default_columns = (
            "name",
            "description",
        )
