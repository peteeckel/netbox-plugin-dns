from netaddr import IPNetwork

from django.test import TestCase
from django.core.exceptions import ValidationError

from ipam.models import IPAddress, Prefix, VRF

from netbox_dns.models import View, Zone, NameServer, Record
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.utilities import get_views_by_prefix, get_ip_addresses_by_prefix


class AutoDNSZoneTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.views = [
            View(name="view1"),
            View(name="view2"),
        ]
        View.objects.bulk_create(cls.views)

        cls.zones = [
            Zone(
                name="zone1.example.com",
                **cls.zone_data,
            ),
        ]
        for zone in cls.zones:
            zone.save()

        cls.prefixes = (
            Prefix(prefix="10.0.0.0/8"),
            Prefix(prefix="10.0.0.0/16"),
            Prefix(prefix="10.0.0.0/24"),
            Prefix(prefix="10.0.1.0/24"),
        )
        Prefix.objects.bulk_create(cls.prefixes)

    def test_update_zone_view_remove_records(self):
        self.views[0].prefixes.add(self.prefixes[2])
        self.views[0].prefixes.add(self.prefixes[3])

        self.zones[0].view = self.views[0]
        self.zones[0].save()

        ip_addresses = (
            IPAddress(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.0.2/24"), dns_name="name2.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.1.1/24"), dns_name="name3.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.1.2/24"), dns_name="name4.zone1.example.com"
            ),
        )
        for ip_address in ip_addresses:
            ip_address.save()
            self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.zones[0].view = self.views[1]
        self.zones[0].save()

        for ip_address in ip_addresses:
            self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())

    def test_update_zone_view_update_records(self):
        self.views[0].prefixes.add(self.prefixes[2])
        self.views[1].prefixes.add(self.prefixes[3])

        self.zones[0].view = self.views[0]
        self.zones[0].save()

        ip_addresses = (
            IPAddress(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.0.2/24"), dns_name="name2.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.1.1/24"), dns_name="name3.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("10.0.1.2/24"), dns_name="name4.zone1.example.com"
            ),
        )
        for ip_address in ip_addresses:
            ip_address.save()

        for ip_address in ip_addresses[0:2]:
            record = Record.objects.get(ipam_ip_address=ip_address)
            self.assertEqual(record.fqdn.rstrip("."), str(ip_address.dns_name))
            self.assertEqual(record.value, str(ip_address.address.ip))
            self.assertEqual(record.zone, self.zones[0])
        for ip_address in ip_addresses[2:4]:
            self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.zones[0].view = self.views[1]
        self.zones[0].save()

        for ip_address in ip_addresses[0:2]:
            self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())
        for ip_address in ip_addresses[2:4]:
            record = Record.objects.get(ipam_ip_address=ip_address)
            self.assertEqual(record.fqdn.rstrip("."), str(ip_address.dns_name))
            self.assertEqual(record.value, str(ip_address.address.ip))
            self.assertEqual(record.zone, self.zones[0])

    def test_delete_zone_remove_records(self):
        self.views[0].prefixes.add(self.prefixes[0])

        self.zones[0].view = self.views[0]
        self.zones[0].save()

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertTrue(
            Record.objects.filter(
                ipam_ip_address=ip_address, zone=self.zones[0]
            ).exists()
        )

        self.zones[0].delete()

        self.assertFalse(
            Record.objects.filter(
                fqdn="name1.zone1.example.com.", value=str(ip_address.address.ip)
            ).exists()
        )

    def test_create_zone_migrate_records(self):
        self.views[0].prefixes.add(self.prefixes[0])

        self.zones[0].view = self.views[0]
        self.zones[0].save()

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.sub1.zone1.example.com"
        )

        self.assertTrue(
            Record.objects.filter(
                ipam_ip_address=ip_address, zone=self.zones[0]
            ).exists()
        )

        child_zone = Zone.objects.create(
            name="sub1.zone1.example.com", view=self.views[0], **self.zone_data
        )

        record = Record.objects.get(
            fqdn="name1.sub1.zone1.example.com.", type=RecordTypeChoices.A
        )
        self.assertEqual(record.zone, child_zone)

    def test_delete_zone_migrate_records(self):
        self.views[0].prefixes.add(self.prefixes[0])

        self.zones[0].view = self.views[0]
        self.zones[0].save()

        parent_zone = Zone.objects.create(
            name="example.com", view=self.views[0], **self.zone_data
        )

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertTrue(
            Record.objects.filter(
                ipam_ip_address=ip_address, zone=self.zones[0]
            ).exists()
        )

        self.zones[0].delete()

        self.assertTrue(
            Record.objects.filter(ipam_ip_address=ip_address, zone=parent_zone).exists()
        )
