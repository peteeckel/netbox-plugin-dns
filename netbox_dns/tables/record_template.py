import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import RecordTemplate
from netbox_dns.utilities import value_to_unicode


__all__ = (
    "RecordTemplateTable",
    "RecordTemplateDisplayTable",
)


class RecordTemplateTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    record_name = tables.Column()
    type = tables.Column()
    value = tables.TemplateColumn(
        template_code="{{ value|truncatechars:64 }}",
    )
    unicode_value = tables.TemplateColumn(
        verbose_name="Unicode Value",
        template_code="{{ value|truncatechars:64 }}",
        accessor="value",
    )
    ttl = tables.Column(
        verbose_name="TTL",
    )
    disable_ptr = tables.BooleanColumn(
        verbose_name="Disable PTR",
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:recordtemplate_list",
    )

    def render_unicode_value(self, value):
        return value_to_unicode(value)

    class Meta(NetBoxTable.Meta):
        model = RecordTemplate
        fields = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
            "unicode_value",
            "status",
            "disable_ptr",
            "tags",
            "description",
            "tenant",
            "tenant_group",
        )
        default_columns = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
            "tags",
        )


class RecordTemplateDisplayTable(RecordTemplateTable):
    actions = ActionsColumn(actions="")

    class Meta(NetBoxTable.Meta):
        model = RecordTemplate
        fields = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
            "unicode_value",
            "status",
            "disable_ptr",
            "description",
        )
        default_columns = (
            "name",
            "record_name",
            "ttl",
            "type",
            "value",
        )
