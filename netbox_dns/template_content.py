from packaging import version
from django.conf import settings

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config
from extras.plugins import PluginTemplateExtension

from netbox_dns.models import Record, RecordTypeChoices, Zone, View, NameServer
from netbox_dns.tables import RelatedRecordTable


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


class RelatedDNSObjects(PluginTemplateExtension):
    model = "tenancy.tenant"

    def left_page(self):
        obj = self.context.get("object")
        request = self.context.get("request")

        related_dns_models = (
            (
                View.objects.restrict(request.user, "view").filter(tenant=obj),
                "tenant_id",
            ),
            (
                NameServer.objects.restrict(request.user, "view").filter(tenant=obj),
                "tenant_id",
            ),
            (
                Zone.objects.restrict(request.user, "view").filter(tenant=obj),
                "tenant_id",
            ),
            (
                Record.objects.restrict(request.user, "view").filter(tenant=obj),
                "tenant_id",
            ),
        )

        return self.render(
            "netbox_dns/related_dns_objects.html",
            extra_context={
                "related_dns_models": related_dns_models,
            },
        )


template_extensions = list()

if version.parse(settings.VERSION) < version.parse("3.7.0"):
    template_extensions.append(RelatedDNSObjects)

if get_plugin_config("netbox_dns", "feature_ipam_coupling"):
    template_extensions.append(RelatedDNSRecords)
elif get_plugin_config("netbox_dns", "feature_ipam_dns_info"):
    template_extensions.append(IPRelatedDNSRecords)
