import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, TagColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import NameServer


__all__ = ("NameServerTable",)


class NameServerTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = NameServer

        fields = ("description",)

        default_columns = (
            "name",
            "tags",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:nameserver_list",
    )

    def render_name(self, value, record):
        return record.display_name
