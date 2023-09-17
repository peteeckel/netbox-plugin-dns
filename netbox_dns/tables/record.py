import django_tables2 as tables

from netbox.tables import (
    NetBoxTable,
    ChoiceFieldColumn,
    ToggleColumn,
    TagColumn,
    ActionsColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import Record
from netbox_dns.utilities import value_to_unicode


class RecordBaseTable(TenancyColumnsMixin, NetBoxTable):
    zone = tables.Column(
        linkify=True,
    )
    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
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
    active = tables.BooleanColumn(
        verbose_name="Active",
    )

    def render_name(self, value, record):
        return record.display_name

    def render_unicode_value(self, value):
        return value_to_unicode(value)


class RecordTable(RecordBaseTable):
    pk = ToggleColumn()
    status = ChoiceFieldColumn()
    disable_ptr = tables.BooleanColumn(
        verbose_name="Disable PTR",
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:record_list",
    )
    ptr_record = tables.Column(
        verbose_name="PTR Record",
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = Record
        fields = (
            "pk",
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "unicode_value",
            "status",
            "disable_ptr",
            "ptr_record",
            "tags",
            "active",
            "description",
            "tenant",
            "tenant_group",
        )
        default_columns = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "tags",
            "active",
        )


class ManagedRecordTable(RecordBaseTable):
    address_record = tables.Column(
        verbose_name="Address Record",
        linkify=True,
    )
    actions = ActionsColumn(actions=("changelog",))

    class Meta(NetBoxTable.Meta):
        model = Record
        fields = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "unicode_value",
            "address_record",
            "active",
        )
        default_columns = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "active",
        )


class RelatedRecordTable(RecordBaseTable):
    actions = ActionsColumn(actions=())

    class Meta(NetBoxTable.Meta):
        model = Record
        fields = (
            "name",
            "zone",
            "type",
            "value",
            "unicode_value",
        )
        default_columns = (
            "name",
            "zone",
            "type",
            "value",
        )
