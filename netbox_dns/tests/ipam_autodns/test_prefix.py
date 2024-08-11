from netaddr import IPNetwork

from django.test import TestCase
from django.core.exceptions import ValidationError

from ipam.models import IPAddress, Prefix, VRF

from netbox_dns.models import View, Zone, NameServer, Record
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.utilities import get_views_by_prefix, get_ip_addresses_by_prefix


class AutoDNSPrefixTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
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
                **zone_data,
                view=cls.views[0],
            ),
            Zone(
                name="zone1.example.com",
                **zone_data,
                view=cls.views[1],
            ),
        ]
        for zone in cls.zones:
            zone.save()

        cls.vrfs = (
            VRF(name="vrf1"),
            VRF(name="vrf2"),
        )
        VRF.objects.bulk_create(cls.vrfs)

        cls.prefixes = (
            Prefix(prefix="10.0.0.0/8"),
            Prefix(prefix="10.0.0.0/16"),
            Prefix(prefix="10.0.0.0/24"),
            Prefix(prefix="10.0.1.0/24"),
        )
        Prefix.objects.bulk_create(cls.prefixes)

    def test_update_prefix_prefix(self):
        prefix = self.prefixes[0]
        view = self.views[0]
        view.prefixes.add(prefix)

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertEqual(view.prefixes.count(), 1)
        self.assertEqual(view.prefixes.first(), prefix)
        self.assertEqual(prefix.netbox_dns_views.first(), view)
        self.assertTrue(Record.objects.filter(fqdn="name1.zone1.example.com.").exists())

        prefix.prefix = "10.0.0.0/12"
        with self.assertRaises(ValidationError):
            prefix.save()

        view.refresh_from_db()
        self.assertTrue(prefix.netbox_dns_views.exists())
        self.assertEqual(view.prefixes.first(), prefix)
        self.assertTrue(Record.objects.filter(fqdn="name1.zone1.example.com.").exists())

    def test_update_prefix_vrf(self):
        prefix = self.prefixes[0]
        view = self.views[0]
        view.prefixes.add(prefix)

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        self.assertEqual(view.prefixes.count(), 1)
        self.assertEqual(view.prefixes.first(), prefix)
        self.assertEqual(prefix.netbox_dns_views.first(), view)
        self.assertTrue(Record.objects.filter(fqdn="name1.zone1.example.com.").exists())

        prefix.vrf = self.vrfs[0]
        with self.assertRaises(ValidationError):
            prefix.save()

        view.refresh_from_db()
        self.assertTrue(prefix.netbox_dns_views.exists())
        self.assertEqual(view.prefixes.first(), prefix)
        self.assertTrue(Record.objects.filter(fqdn="name1.zone1.example.com.").exists())

    def test_update_prefix_view(self):
        prefix = self.prefixes[0]
        self.views[0].prefixes.add(prefix)

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )

        record = Record.objects.get(
            fqdn="name1.zone1.example.com.", type=RecordTypeChoices.A
        )
        self.assertEqual(record.zone, self.zones[0])

        self.views[0].prefixes.remove(prefix)
        self.views[1].prefixes.add(prefix)

        record = Record.objects.get(
            fqdn="name1.zone1.example.com.", type=RecordTypeChoices.A
        )
        self.assertEqual(record.zone, self.zones[1])

    def test_create_prefix(self):
        prefix = Prefix.objects.create(prefix="10.1.0.0/16")

        self.assertFalse(prefix.netbox_dns_views.exists())
        self.assertEqual(set(get_views_by_prefix(prefix)), set())

    def test_create_prefix_inherit_views(self):
        self.views[0].prefixes.add(self.prefixes[0])
        self.views[1].prefixes.add(self.prefixes[0])

        prefix = Prefix.objects.create(prefix="10.1.0.0/16")

        self.assertFalse(prefix.netbox_dns_views.exists())
        self.assertEqual(set(get_views_by_prefix(prefix)), set(self.views))

    def test_delete_prefix_with_view(self):
        self.views[0].prefixes.add(self.prefixes[0])
        self.views[1].prefixes.add(self.prefixes[1])

        self.assertEqual(set(get_views_by_prefix(self.prefixes[2])), {self.views[1]})

        self.prefixes[1].delete()

        self.assertEqual(set(get_views_by_prefix(self.prefixes[2])), {self.views[0]})

    def test_delete_prefix_without_view(self):
        self.views[0].prefixes.add(self.prefixes[0])

        self.assertEqual(set(get_views_by_prefix(self.prefixes[1])), {self.views[0]})
        self.assertEqual(set(get_views_by_prefix(self.prefixes[2])), {self.views[0]})

        self.prefixes[1].delete()

        self.assertEqual(set(get_views_by_prefix(self.prefixes[2])), {self.views[0]})

    def test_delete_prefix_with_view_dns_conflict(self):
        self.views[0].prefixes.add(self.prefixes[0])
        self.views[1].prefixes.add(self.prefixes[1])

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        # +
        # Deleting prefix 10.0.0.0/16 results in the inherited view of 10.0.0.24
        # changing to "view1". This causes a conflict with the non-managed A record
        # in that zone.
        # -
        with self.assertRaises(ValidationError):
            self.prefixes[1].delete()
