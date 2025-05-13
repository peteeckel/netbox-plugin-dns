import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


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
    "DelegationRecordTable",
)


class RecordBaseTable(TenancyColumnsMixin, NetBoxTable):
    zone = tables.Column(
        verbose_name=_("Zone"),
        linkify=True,
    )
    view = tables.Column(
        verbose_name=_("View"),
        accessor="zone__view",
        linkify=True,
    )
    type = tables.Column(
        verbose_name=_("Type"),
    )
    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    fqdn = tables.Column(
        verbose_name=_("FQDN"),
        linkify=True,
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
    active = tables.BooleanColumn(
        verbose_name=_("Active"),
    )

    def render_name(self, value, record):
        return record.display_name

    def render_unicode_value(self, value):
        return value_to_unicode(value)


class RecordTable(RecordBaseTable):
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

    status = ChoiceFieldColumn(
        verbose_name=_("Status"),
    )
    disable_ptr = tables.BooleanColumn(
        verbose_name=_("Disable PTR"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:record_list",
    )
    ptr_record = tables.Column(
        verbose_name=_("PTR Record"),
        linkify=True,
    )


class ManagedRecordTable(RecordBaseTable):
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

    address_records = tables.ManyToManyColumn(
        verbose_name=_("Address Records"),
        linkify=True,
        linkify_item=True,
        transform=lambda obj: (
            obj.fqdn.rstrip(".")
            if obj.zone.view.default_view
            else f"[{obj.zone.view.name}] {obj.fqdn.rstrip('.')}"
        ),
    )
    ipam_ip_address = tables.Column(
        verbose_name=_("IPAM IP Address"),
        linkify=True,
    )
    related_ip_address = tables.Column(
        verbose_name=_("Related IP Address"),
        empty_values=(),
        orderable=False,
    )
    actions = ActionsColumn(actions=("changelog",))

    def render_related_ip_address(self, record):
        if record.ipam_ip_address is not None:
            address = record.ipam_ip_address
        elif hasattr(record, "address_records"):
            address_record = record.address_records.filter(
                ipam_ip_address__isnull=False
            ).first()
            if address_record is not None:
                address = address_record.ipam_ip_address
            else:
                address = None

        if address is None:
            return format_html("&mdash;")

        return format_html(f"<a href='{address.get_absolute_url()}'>{address}</a>")

    def value_related_ip_address(self, record):
        if record.ipam_ip_address is not None:
            return record.ipam_ip_address
        elif hasattr(record, "address_records"):
            address_record = record.address_records.filter(
                ipam_ip_address__isnull=False
            ).first()
            if address_record is not None:
                return address_record.ipam_ip_address

            return None


class RelatedRecordTable(RecordBaseTable):
    class Meta(NetBoxTable.Meta):
        model = Record

        fields = ()

        default_columns = (
            "name",
            "zone",
            "type",
            "value",
        )

    actions = ActionsColumn(actions=())


class DelegationRecordTable(RecordBaseTable):
    class Meta(NetBoxTable.Meta):
        model = Record

        fields = ()

        default_columns = (
            "name",
            "zone",
            "type",
            "value",
        )
