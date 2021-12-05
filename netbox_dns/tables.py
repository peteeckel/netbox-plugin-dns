import django_tables2 as tables

from utilities.tables import BaseTable, ChoiceFieldColumn, ToggleColumn, TagColumn
from .models import NameServer, Record, Zone


class ZoneTable(BaseTable):
    """Table for displaying Zone objects."""

    pk = ToggleColumn()
    name = tables.Column(
        linkify=True,
    )
    soa_mname = tables.Column(
        linkify=True,
    )
    status = ChoiceFieldColumn()
    tags = TagColumn(
        url_name="plugins:netbox_dns:zone_list",
    )
    default_ttl = tables.Column(
        verbose_name="Default TTL",
    )

    class Meta(BaseTable.Meta):
        model = Zone
        fields = (
            "pk",
            "name",
            "status",
            "tags",
            "default_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial",
        )
        default_columns = (
            "pk",
            "name",
            "status",
            "tags",
        )


class NameServerTable(BaseTable):
    """Table for displaying NameServer objects."""

    pk = ToggleColumn()
    name = tables.Column(
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:nameserver_list",
    )

    class Meta(BaseTable.Meta):
        model = NameServer
        fields = (
            "pk",
            "name",
            "tags",
        )


class RecordTable(BaseTable):
    """Table for displaying Record objects."""

    pk = ToggleColumn()
    zone = tables.Column(
        linkify=True,
    )
    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
    disable_ptr = tables.BooleanColumn(
        verbose_name="Disable PTR",
    )
    ttl = tables.Column(
        verbose_name="TTL",
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:record_list",
    )
    ptr_record = tables.Column(
        verbose_name="PTR Record",
        linkify=True,
    )

    class Meta(BaseTable.Meta):
        model = Record
        fields = (
            "pk",
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "disable_ptr",
            "ptr_record",
            "tags",
        )
        default_columns = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "tags",
        )


class ManagedRecordTable(BaseTable):
    """Table for displaying managed Record objects."""

    zone = tables.Column(
        linkify=True,
    )
    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
    ttl = tables.Column(
        verbose_name="TTL",
    )
    address_record = tables.Column(
        verbose_name="Address Record",
        linkify=True,
    )

    class Meta(BaseTable.Meta):
        model = Record
        fields = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
            "address_record",
        )
        default_columns = (
            "zone",
            "name",
            "ttl",
            "type",
            "value",
        )


class ZoneRecordTable(BaseTable):
    """Table for displaying Record objects for a given zone."""

    pk = ToggleColumn()
    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
    ttl = tables.Column(
        verbose_name="TTL",
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:record_list",
    )
    ptr_record = tables.Column(
        verbose_name="PTR Record",
        linkify=True,
    )

    class Meta(BaseTable.Meta):
        model = Record
        fields = (
            "pk",
            "name",
            "ttl",
            "type",
            "value",
            "disable_ptr",
            "ptr_record",
            "tags",
        )


class ZoneManagedRecordTable(BaseTable):
    """Table for displaying managed Record objects for a given zone."""

    type = tables.Column()
    name = tables.Column(
        linkify=True,
    )
    ttl = tables.Column(
        verbose_name="TTL",
    )
    address_record = tables.Column(
        linkify=True,
    )

    class Meta(BaseTable.Meta):
        model = Record
        fields = (
            "name",
            "ttl",
            "type",
            "value",
            "address_record",
        )
