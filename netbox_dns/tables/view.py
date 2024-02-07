import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import View


class ViewTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(url_name="plugins:netbox_dns:view_list")

    class Meta(NetBoxTable.Meta):
        model = View
        fields = ("name", "description", "tenant", "tenant_group", "tags")
        default_columns = ("name",)
