import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ipam.tables import PrefixTable
from utilities.tables import register_table_column

views = tables.ManyToManyColumn(
    verbose_name=_("DNS Views"),
    linkify_item=True,
)

register_table_column(views, "netbox_dns_views", PrefixTable)
