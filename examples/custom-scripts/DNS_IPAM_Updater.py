#!/usr/bin/env python3

import dns
from dns import name as dns_name

from netbox_dns.models import Record, View, RecordTypeChoices, Zone
from ipam.models import IPAddress, VRF

from extras.scripts import Script, ObjectVar, BooleanVar

name = "NetBox DNS IPAM Import/Export"


class IPAMHostnameUpdater(Script):
    class Meta:
        name = "IPAM Hostname Updater"
        description = "Update the 'DNS Host' field in IPAM from NetBox DNS PTR records"
        commit_default = True

    vrf = ObjectVar(
        model=VRF,
        label="IPAM VRF",
        required=False,
    )

    view = ObjectVar(
        model=View,
        label="DNS View",
        required=True,
    )

    overwrite = BooleanVar(
        description="Overwrite existing DNS Names in IPAM",
        default=False,
    )

    def run(self, data, commit):
        if data["vrf"] is None:
            ip_object_filter = {"vrf__isnull": True}
        else:
            ip_object_filter = {"vrf": data["vrf"]}

        record_filter = {"zone__view": data["view"]}

        ip_addresses = IPAddress.objects.filter(**ip_object_filter)
        for ip_address in ip_addresses:
            if ip_address.address.version == 4:
                record_type = RecordTypeChoices.A
            else:
                record_type = RecordTypeChoices.AAAA

            try:
                address_record = Record.objects.get(type=record_type, ip_address=ip_address.address.ip, **record_filter)
                hostname = address_record.fqdn.rstrip(".")
            except Record.DoesNotExist:
                self.log_info(f"No address record found for {ip_address}")
                continue
            except Record.MultipleObjectsReturned:
                self.log_warning(f"Multiple address records found for {ip_address}")
                continue

            if hostname != ip_address.dns_name:
                if not data["overwrite"]:
                    self.log_info(f"Not overwriting exitsing value {ip_address.dns_name} with DNS name {hostname}")
                    continue

                self.log_info(hostname)
                self.log_info(ip_address.dns_name)
                self.log_info(f"Updating DNS name for {ip_address} to {hostname}")

                if hasattr(ip_address, "snapshot"):
                    ip_address.snapshot()

                    ip_address.dns_name = hostname
                    ip_address.full_clean()
                    ip_address.save()


class DNSRecordUpdater(Script):
    class Meta:
        name = "DNS Name Record Updater"
        description = "Create or update DNS address records from IPAM 'DNS Name' fields"
        commit_default = True

    vrf = ObjectVar(
        model=VRF,
        label="IPAM VRF",
        required=False,
    )

    view = ObjectVar(
        model=View,
        label="DNS View",
        required=True,
    )

    overwrite = BooleanVar(
        description="Overwrite existing DNS address records",
        default=False,
    )

    def run(self, data, commit):
        if data["vrf"] is None:
            ip_addresses = IPAddress.objects.filter(vrf__isnull=True).exclude(dns_name="")
        else:
            ip_addresses = IPAddress.objects.filter(vrf=data["vrf"]).exclude(dns_name="")

        for ip_address in ip_addresses:
            address = ip_address.address.ip
            try:
                fqdn = dns_name.from_text(ip_address.dns_name, origin=dns_name.root)
            except dns.exception.DNSException as exc:
                self.log_info(f"{ip_address.dns_name} is not a valid domain name")

            zone = fqdn.parent()

            try:
                zone_object = Zone.objects.get(name=str(zone).rstrip("."), view=data["view"])
            except Zone.DoesNotExist:
                self.log_warning(f"Zone {zone} does not exist, cannot create or update record")

            name = fqdn.relativize(zone).to_text()

            if ip_address.address.version == 4:
                record_type = RecordTypeChoices.A
            else:
                record_type = RecordTypeChoices.AAAA

            record_filter = {
                "ip_address": address,
                "type": record_type,
            }

            record_filter["zone__view"] = data["view"]

            try:
                address_record = Record.objects.get(**record_filter)
            except Record.MultipleObjectsReturned:
                self.log_warning(f"Multiple {record_type} records found for {ip_address}")
                continue
            except Record.DoesNotExist:
                self.log_info(f"Creating a new {record_type} record {fqdn} for {ip_address}")
                Record(
                    name=name,
                    zone=zone_object,
                    type=record_type,
                    value=str(address),
                ).save()
                continue

            if address_record.fqdn != str(fqdn):
                if data["overwrite"]:
                    self.log_info(f"Updating {record_type} record for {ip_address} with new name {fqdn}")
                    if hasattr(address_record, "snapshot"):
                        address_record.snapshot()

                    address_record.zone = zone_object
                    address_record.name = name
                    address_record.save()
                else:
                    self.log_info(
                        f"Not overwriting {record_type} record {address_record.fqdn} for {ip_address} with new name {fqdn}"
                    )
