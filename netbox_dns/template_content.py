from netbox.plugins.utils import get_plugin_config
from netbox.plugins import PluginTemplateExtension

from netbox_dns.models import Record, Zone, View, NameServer
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.tables import RelatedRecordTable, RelatedViewTable


class RelatedDNSRecords(PluginTemplateExtension):
    model = "ipam.ipaddress"

    def right_page(self):
        ip_address = self.context.get("object")

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
        else:
            address_record_table = None

        if pointer_records:
            pointer_record_table = RelatedRecordTable(
                data=pointer_records,
            )
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
    model = "ipam.prefix"

    def right_page(self):
        prefix = self.context.get("object")

        views = prefix.netbox_dns_views.all()

        if views:
            view_table = RelatedViewTable(
                data=views,
            )
        else:
            view_table = None

        return self.render(
            "netbox_dns/view/related.html",
            extra_context={
                "related_views": view_table,
            },
        )


class IPRelatedDNSRecords(PluginTemplateExtension):
    model = "ipam.ipaddress"

    def right_page(self):
        ip_address = self.context.get("object")

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
        else:
            address_record_table = None

        if pointer_records:
            pointer_record_table = RelatedRecordTable(
                data=pointer_records,
            )
        else:
            pointer_record_table = None

        return self.render(
            "netbox_dns/record/related.html",
            extra_context={
                "related_address_records": address_record_table,
                "related_pointer_records": pointer_record_table,
            },
        )


template_extensions = [RelatedDNSRecords, RelatedDNSViews]

if get_plugin_config("netbox_dns", "feature_ipam_dns_info"):
    template_extensions.append(IPRelatedDNSRecords)
