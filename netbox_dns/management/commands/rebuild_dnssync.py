from django.core.management.base import BaseCommand

from ipam.models import IPAddress

from netbox_dns.utilities import update_dns_records, get_zones


class Command(BaseCommand):
    help = "Rebuild DNSsync relationships between IP addresses and records"

    def handle(self, *model_names, **options):
        ip_addresses = IPAddress.objects.all()
        for ip_address in ip_addresses:
            if options.get("verbosity") >= 2:
                self.stdout.write(
                    f"Updating DNS records for IP Address {ip_address}, VRF {ip_address.vrf}"
                )
            if options.get("verbosity") >= 3:
                self.stdout.write(f"  Zones: {get_zones(ip_address)}")
            if update_dns_records(ip_address) and options.get("verbosity") >= 1:
                self.stdout.write(
                    f"Updated DNS records for IP Address {ip_address}, VRF {ip_address.vrf}"
                )
