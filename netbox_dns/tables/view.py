import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import View


__all__ = (
    "ViewTable",
    "RelatedViewTable",
)


class ViewTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    default_view = tables.BooleanColumn(
        verbose_name="Default View",
    )
    tags = TagColumn(url_name="plugins:netbox_dns:view_list")

    class Meta(NetBoxTable.Meta):
        model = View
        fields = (
            "name",
            "default_view",
            "description",
            "tenant",
            "tenant_group",
            "tags",
        )
        default_columns = ("name", "default_view")


class RelatedViewTable(TenancyColumnsMixin, NetBoxTable):
    actions = ActionsColumn(actions=())

    name = tables.Column(
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = View
        fields = (
            "name",
            "description",
            "tenant",
            "tenant_group",
            "tags",
        )
        default_columns = ("name", "description")
