from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, View, Zone


class RFC2317ZoneTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zone_data = {
            "default_ttl": 86400,
            "soa_mname": cls.nameserver,
            "soa_rname": "hostmaster.example.com",
            "soa_refresh": 172800,
            "soa_retry": 7200,
            "soa_expire": 2592000,
            "soa_ttl": 86400,
            "soa_minimum": 3600,
            "soa_serial": 1,
            "soa_serial_auto": False,
        }

        cls.views = (
            View(name="internal"),
            View(name="external"),
        )
        View.objects.bulk_create(cls.views)

    def test_create_rfc2317_zone_parent_unmanaged(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28"
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertFalse(zone1.rfc2317_child_zones.exists())

    def test_create_rfc2317_zone_parent_unmanaged_no_parent(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28"
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)

    def test_create_rfc2317_zone_parent_managed(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

    def test_create_rfc2317_zone_invalid_prefix_length(self):
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0-255.0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.0/24"
            )

    def test_create_rfc2317_zone_invalid_prefix_no_network(self):
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0-15.0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.1/28"
            )

    def test_create_rfc2317_zone_parent_managed_no_parent(self):
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0-15.0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.0/28",
                rfc2317_parent_managed=True
            )

    def test_create_rfc2317_zone_parent_managed_arpa_zone(self):
        zone1 = Zone.objects.create(name="0.10.in-addr.arpa", **self.zone_data)
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.0/28",
                rfc2317_parent_managed=True
            )

    def test_create_rfc2317_zone_parent_managed_no_view(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[0]
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertNotIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_create_rfc2317_zone_parent_managed_view(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[0]
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
            view=self.views[0]
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertNotIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_create_rfc2317_zone_parent_managed_different_view(self):
        zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[0]
        )
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[1]
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
            view=self.views[0]
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertNotIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_create_rfc2317_zone_parent_managed_different_no_matching_view(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[1]
        )
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0-15.0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.0/28",
                rfc2317_parent_managed=True,
                view=self.views[0]
            )

    def test_create_rfc2317_zone_parent_managed_different_no_null_view(self):
        zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[0]
        )
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[1]
        )
        with self.assertRaises(ValidationError):
            Zone.objects.create(
                name="0-15.0.0.10.in-addr.arpa",
                **self.zone_data,
                rfc2317_prefix="10.0.0.0/28",
                rfc2317_parent_managed=True
            )

    def test_modify_rfc2317_zone_parent_managed_change_prefix(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(name="1.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertNotIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

        rfc2317_zone.rfc2317_prefix = "10.0.1.0/28"
        rfc2317_zone.save()

        self.assertNotIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_modify_rfc2317_zone_parent_managed_change_view(self):
        zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[0]
        )
        zone2 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data, view=self.views[1]
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
            view=self.views[0]
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertFalse(zone2.rfc2317_child_zones.exists())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

        rfc2317_zone.view = self.views[1]
        rfc2317_zone.save()

        self.assertFalse(zone1.rfc2317_child_zones.exists())
        self.assertIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertNotEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_modify_rfc2317_zone_set_unmanaged(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

        rfc2317_zone.rfc2317_parent_managed = False
        rfc2317_zone.save()

        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertFalse(zone1.rfc2317_child_zones.exists())

    def test_modify_rfc2317_zone_set_managed(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28"
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertFalse(zone1.rfc2317_child_zones.exists())

        rfc2317_zone.rfc2317_parent_managed = True
        rfc2317_zone.save()

        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

    def test_delete_rfc2317_zone(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

        rfc2317_zone.delete()

        self.assertFalse(zone1.rfc2317_child_zones.exists())

    def test_delete_parent_zone(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

        zone1.delete()
        rfc2317_zone.refresh_from_db()

        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertEqual(str(rfc2317_zone.rfc2317_prefix), "10.0.0.0/28")

    def test_delete_parent_zone_new_parent(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(name="0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

        zone1.delete()
        rfc2317_zone.refresh_from_db()

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)

    def test_create_parent_zone_new_parent(self):
        zone1 = Zone.objects.create(name="0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)

        zone2 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone.refresh_from_db()

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone2.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)
