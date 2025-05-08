import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import View


__all__ = (
    "ViewTable",
    "RelatedViewTable",
)


class ViewTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = View

        fields = (
            "description",
            "ip_address_filter",
        )

        default_columns = (
            "name",
            "default_view",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    default_view = tables.BooleanColumn(
        verbose_name=_("Default View"),
    )
    tags = TagColumn(url_name="plugins:netbox_dns:view_list")


class RelatedViewTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = View

        fields = (
            "name",
            "description",
            "tenant",
            "tenant_group",
            "tags",
        )

        default_columns = (
            "name",
            "description",
        )

    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(url_name="plugins:netbox_dns:view_list")
    actions = ActionsColumn(actions=())
