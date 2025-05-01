import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import RecordTemplate
from netbox_dns.utilities import value_to_unicode


__all__ = (
    "RecordTemplateTable",
    "RecordTemplateDisplayTable",
)


class RecordTemplateTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = RecordTemplate

        fields = (
            "status",
            "description",
        )

        default_columns = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
            "tags",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    record_name = tables.Column(
        verbose_name=_("Record Name"),
    )
    type = tables.Column(
        verbose_name=_("Type"),
    )
    value = tables.TemplateColumn(
        verbose_name=_("Value"),
        template_code="{{ value|truncatechars:64 }}",
    )
    unicode_value = tables.TemplateColumn(
        verbose_name=_("Unicode Value"),
        template_code="{{ value|truncatechars:64 }}",
        accessor="value",
    )
    ttl = tables.Column(
        verbose_name=_("TTL"),
    )
    disable_ptr = tables.BooleanColumn(
        verbose_name=_("Disable PTR"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:recordtemplate_list",
    )

    def render_unicode_value(self, value):
        return value_to_unicode(value)


class RecordTemplateDisplayTable(RecordTemplateTable):
    class Meta(NetBoxTable.Meta):
        model = RecordTemplate

        fields = (
            "status",
            "description",
        )

        default_columns = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
        )

    actions = ActionsColumn(actions="")
