import django_tables2 as tables

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.plugins.utils import get_plugin_config
from netbox.plugins import PluginTemplateExtension
from utilities.tables import register_table_column
from ipam.tables import IPAddressTable

from netbox_dns.models import Record
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.tables import RelatedRecordTable, RelatedViewTable
from netbox_dns.utilities import get_views_by_prefix


class RelatedDNSRecords(PluginTemplateExtension):
    models = ("ipam.ipaddress",)

    def right_page(self):
        ip_address = self.context.get("object")
        request = self.context.get("request")

        address_records = ip_address.netbox_dns_records.all()
        pointer_records = [
            address_record.ptr_record
            for address_record in address_records
            if address_record.ptr_record is not None
        ]

        if address_records:
            address_record_table = RelatedRecordTable(
                data=address_records,
            )
            address_record_table.configure(request)
        else:
            address_record_table = None

        if pointer_records:
            pointer_record_table = RelatedRecordTable(
                data=pointer_records,
            )
            pointer_record_table.configure(request)
        else:
            pointer_record_table = None

        return self.render(
            "netbox_dns/record/related.html",
            extra_context={
                "related_address_records": address_record_table,
                "related_pointer_records": pointer_record_table,
            },
        )


class RelatedDNSViews(PluginTemplateExtension):
    models = ("ipam.prefix",)

    def right_page(self):
        prefix = self.context.get("object")
        request = self.context.get("request")

        if assigned_views := prefix.netbox_dns_views.all():
            assigned_views_table = RelatedViewTable(data=assigned_views)
            assigned_views_table.configure(request)
            context = {"assigned_views": assigned_views_table}
        elif inherited_views := get_views_by_prefix(prefix):
            inherited_views_table = RelatedViewTable(data=inherited_views)
            inherited_views_table.configure(request)
            context = {"inherited_views": inherited_views_table}
        else:
            context = {}

        return self.render(
            "netbox_dns/view/related.html",
            extra_context=context,
        )

    def buttons(self):
        return self.render(
            "netbox_dns/view/button.html",
            extra_context={
                "url": reverse(
                    "ipam:prefix_views",
                    kwargs={"pk": self.context.get("object").pk},
                ),
            },
        )


class IPRelatedDNSRecords(PluginTemplateExtension):
    models = ("ipam.ipaddress",)

    def right_page(self):
        ip_address = self.context.get("object")
        request = self.context.get("request")

        address_records = Record.objects.filter(
            type__in=(RecordTypeChoices.A, RecordTypeChoices.AAAA),
            ip_address=ip_address.address.ip,
        )
        pointer_records = Record.objects.filter(
            type=RecordTypeChoices.PTR,
            ip_address=ip_address.address.ip,
        )

        if address_records:
            address_record_table = RelatedRecordTable(
                data=address_records,
            )
            address_record_table.configure(request)
        else:
            address_record_table = None

        if pointer_records:
            pointer_record_table = RelatedRecordTable(
                data=pointer_records,
            )
            pointer_record_table.configure(request)
        else:
            pointer_record_table = None

        return self.render(
            "netbox_dns/record/related.html",
            extra_context={
                "related_address_records": address_record_table,
                "related_pointer_records": pointer_record_table,
            },
        )


address_records = tables.ManyToManyColumn(
    verbose_name=_("DNS Address Records"),
    accessor="netbox_dns_records",
    linkify_item=True,
    transform=lambda obj: (
        obj.fqdn.rstrip(".")
        if obj.zone.view.default_view
        else f"[{obj.zone.view.name}] {obj.fqdn.rstrip('.')}"
    ),
)

if not settings.PLUGINS_CONFIG["netbox_dns"].get("dnssync_disabled"):
    template_extensions = [RelatedDNSRecords, RelatedDNSViews]
    register_table_column(address_records, "address_records", IPAddressTable)
else:
    template_extensions = []

if get_plugin_config("netbox_dns", "feature_ipam_dns_info"):
    template_extensions.append(IPRelatedDNSRecords)
