#!/usr/bin/env python3

from extras.scripts import Script
from ipam.models import IPAddress

from netbox_dns.models import Record
from netbox_dns.choices import RecordTypeChoices

name = "NetBox DNS Tenancy Synchronizer"


class RecordTenancySynchronizer(Script):
    class Meta:
        name = "Record Tenancy Synchronizer"
        description = "Set the tenant for a PTR record from its address record"
        commit_default = True

    def run(self, data, commit):
        self.log_info("Record Tenancy Synchronizer started")

        if (pk := data.get("id")) is None:
            return

        record = Record.objects.get(pk=pk)
        if record.is_address_record:
            if (ptr_record := record.ptr_record) is not None and ptr_record.tenant != record.tenant:
                self.log_info(f"Setting tenant for record {ptr_record} to {record.tenant}")
                ptr_record.tenant = record.tenant
                ptr_record.save()

        self.log_info("Record Tenancy Synchronizer done")


class IPAddressTenancySynchronizer(Script):
    class Meta:
        name = "IP Address Tenancy Synchronizer"
        description = "Set the tenant for an IPAM coupled address record from its IP address"
        commit_default = True

    def run(self, data, commit):
        self.log_info("IP Address Tenancy Synchronizer started")

        if (pk := data.get("id")) is None:
            return

        ip_address = IPAddress.objects.get(pk=pk)
        tenant = ip_address.tenant
        for address_record in ip_address.netbox_dns_records.all():
            if address_record.tenant != tenant:
                self.log_info(f"Setting tenant for record {address_record} to {tenant}")
                address_record.tenant = tenant
                address_record.save()

            if (ptr_record := address_record.ptr_record) is not None and ptr_record.tenant != tenant:
                self.log_info(f"Setting tenant for record {ptr_record} to {tenant}")
                ptr_record.tenant = tenant
                ptr_record.save()

        self.log_info("IP Address Tenancy Synchronizer done")
