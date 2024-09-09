import django_tables2 as tables
from django.utils.html import format_html


from netbox.tables import (
    NetBoxTable,
    ChoiceFieldColumn,
    TagColumn,
    ActionsColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import Record
from netbox_dns.utilities import value_to_unicode


__all__ = (
    "RecordTable",
    "ManagedRecordTable",
    "RelatedRecordTable",
)


class RecordBaseTable(TenancyColumnsMixin, NetBoxTable):
    zone = tables.Column(
        linkify=True,
    )
    view = tables.Column(
        accessor="zone__view",
        linkify=True,
    )
    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
    fqdn = tables.Column(
        verbose_name="FQDN",
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
            "status",
            "description",
        )
        default_columns = (
            "name",
            "zone",
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
    ipam_ip_address = tables.Column(
        verbose_name="IPAM IP Address",
        linkify=True,
    )
    related_ip_address = tables.Column(
        verbose_name="Related IP Address",
        empty_values=(),
        orderable=False,
    )
    actions = ActionsColumn(actions=("changelog",))

    class Meta(NetBoxTable.Meta):
        model = Record
        fields = ()
        default_columns = (
            "name",
            "zone",
            "ttl",
            "type",
            "value",
            "active",
        )

    def render_related_ip_address(self, record):
        if record.ipam_ip_address is not None:
            address = record.ipam_ip_address
        elif (
            hasattr(record, "address_record")
            and record.address_record.ipam_ip_address is not None
        ):
            address = record.address_record.ipam_ip_address
        else:
            return format_html("&mdash;")

        return format_html(f"<a href='{address.get_absolute_url()}'>{address}</a>")

    def value_related_ip_address(self, record):
        if record.ipam_ip_address is not None:
            return record.ipam_ip_address
        elif (
            hasattr(record, "address_record")
            and record.address_record.ipam_ip_address is not None
        ):
            return record.address_record.ipam_ip_address


class RelatedRecordTable(RecordBaseTable):
    actions = ActionsColumn(actions=())

    class Meta(NetBoxTable.Meta):
        model = Record
        fields = ()
        default_columns = (
            "name",
            "zone",
            "type",
            "value",
        )
