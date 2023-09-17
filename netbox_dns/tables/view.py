import django_tables2 as tables

from netbox.tables import NetBoxTable
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import View


class ViewTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = View
        fields = ("name", "description", "tenant", "tenant_group")
        default_columns = ("name",)
