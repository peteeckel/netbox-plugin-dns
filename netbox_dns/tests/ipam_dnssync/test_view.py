from netaddr import IPNetwork

from django.test import TestCase
from django.core import management

from ipam.models import IPAddress, Prefix

from netbox_dns.models import View, Zone, NameServer, Record
from netbox_dns.choices import RecordTypeChoices


class AutoDNSViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.views = (
            View(name="view1"),
            View(name="view2"),
        )
        for view in cls.views:
            view.save()

        cls.zones = (
            Zone(view=cls.views[0], name="zone1.example.com", **cls.zone_data),
            Zone(view=cls.views[1], name="zone1.example.com", **cls.zone_data),
            Zone(view=cls.views[0], name="zone2.example.com", **cls.zone_data),
            Zone(view=cls.views[1], name="zone2.example.com", **cls.zone_data),
        )
        for zone in cls.zones:
            zone.save()

        cls.prefixes = (
            Prefix(prefix="10.0.0.0/24"),
            Prefix(prefix="10.0.1.0/24"),
        )
        Prefix.objects.bulk_create(cls.prefixes)

        cls.views[0].prefixes.add(cls.prefixes[0])
        cls.views[1].prefixes.add(cls.prefixes[1])

        management.call_command("setup_autodns", verbosity=0)

    def test_create_ip_address(self):
        ip_address1 = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ip_address2 = IPAddress.objects.create(
            address=IPNetwork("10.0.1.1/24"), dns_name="name1.zone1.example.com"
        )

        record1 = Record.objects.get(
            type=RecordTypeChoices.A,
            value="10.0.0.1",
            fqdn="name1.zone1.example.com.",
            zone=self.zones[0],
        )
        record2 = Record.objects.get(
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            fqdn="name1.zone1.example.com.",
            zone=self.zones[1],
        )

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 2)
        self.assertEqual(record1.ipam_ip_address, ip_address1)
        self.assertEqual(record2.ipam_ip_address, ip_address2)

    def test_create_ip_address_multiple_views(self):
        self.views[1].prefixes.add(self.prefixes[0])

        ip_address1 = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        record1 = Record.objects.get(
            type=RecordTypeChoices.A,
            value="10.0.0.1",
            fqdn="name1.zone1.example.com.",
            zone=self.zones[0],
        )
        record2 = Record.objects.get(
            type=RecordTypeChoices.A,
            value="10.0.0.1",
            fqdn="name1.zone1.example.com.",
            zone=self.zones[1],
        )

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 2)
        self.assertEqual(record1.ipam_ip_address, ip_address1)
        self.assertEqual(record2.ipam_ip_address, ip_address1)

    def test_create_ip_address_no_view(self):
        self.views[0].prefixes.remove(self.prefixes[0])

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertFalse(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                fqdn="name1.zone1.example.com.",
            ).exists()
        )

    def test_create_ip_address_no_zone_in_view(self):
        self.zones[0].view = View.get_default_view()
        self.zones[0].save()

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertFalse(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                fqdn="name1.zone1.example.com.",
            ).exists()
        )

    def test_update_ip_address_address_change_view(self):
        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )

        ip_address.address = IPNetwork("10.0.1.1/24")
        ip_address.save()

        self.assertFalse(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )
        record = Record.objects.get(
            type=RecordTypeChoices.A,
            fqdn="name1.zone1.example.com.",
            zone=self.zones[1],
        )
        self.assertEqual(record.ipam_ip_address, ip_address)
        self.assertEqual(record.value, str(ip_address.address.ip))

    def test_update_ip_address_address_remove_from_view(self):
        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )

        ip_address.address = IPNetwork("10.0.2.1/24")
        ip_address.save()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())

    def test_update_ip_address_address_remove_from_multiple_views(self):
        self.views[1].prefixes.add(self.prefixes[0])

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 2)
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[1],
            ).exists()
        )

        ip_address.address = IPNetwork("10.0.2.1/24")
        ip_address.save()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())

    def test_update_ip_address_address_add_to_view(self):
        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.2.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())

        ip_address.address = IPNetwork("10.0.0.1/24")
        ip_address.save()

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 1)
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )

    def test_update_ip_address_address_add_to_multiple_views(self):
        self.views[1].prefixes.add(self.prefixes[0])

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.2.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())

        ip_address.address = IPNetwork("10.0.0.1/24")
        ip_address.save()

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 2)
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[1],
            ).exists()
        )

    def test_delete_ip_address_multiple_views(self):
        self.views[1].prefixes.add(self.prefixes[0])

        ip_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertEqual(Record.objects.filter(type=RecordTypeChoices.A).count(), 2)
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[0],
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.A,
                fqdn="name1.zone1.example.com.",
                zone=self.zones[1],
            ).exists()
        )

        ip_address.delete()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())
