from django.conf import settings
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone


@override_settings(
    PLUGINS_CONFIG={
        "netbox_dns": {
            "zone_default_ttl": 10000,
            "zone_soa_ttl": 20000,
            "zone_soa_refresh": 30000,
            "zone_soa_retry": 40000,
            "zone_soa_expire": 50000,
            "zone_soa_minimum": 60000,
            "zone_soa_serial": 70000,
            "zone_soa_rname": "hostmaster.example.com",
            "zone_soa_mname": "ns1.example.com",
        }
    }
)
class ZoneDefaultValuesCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

    def test_default_values(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_serial_auto=False)

        self.assertEqual(zone.default_ttl, 10000)
        self.assertEqual(zone.soa_ttl, 20000)
        self.assertEqual(zone.soa_refresh, 30000)
        self.assertEqual(zone.soa_retry, 40000)
        self.assertEqual(zone.soa_expire, 50000)
        self.assertEqual(zone.soa_minimum, 60000)
        self.assertFalse(zone.soa_serial_auto)
        self.assertEqual(zone.soa_serial, 70000)
        self.assertEqual(zone.soa_rname, "hostmaster.example.com")
        self.assertEqual(zone.soa_mname, self.nameserver)

    def test_override_default_ttl(self):
        zone = Zone.objects.create(name="zone1.example.com", default_ttl=42)

        self.assertEqual(zone.default_ttl, 42)

    def test_override_soa_ttl(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_ttl=42)

        self.assertEqual(zone.soa_ttl, 42)

    def test_override_soa_refresh(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_refresh=42)

        self.assertEqual(zone.soa_refresh, 42)

    def test_override_soa_retry(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_retry=42)

        self.assertEqual(zone.soa_retry, 42)

    def test_override_soa_expire(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_expire=42)

        self.assertEqual(zone.soa_expire, 42)

    def test_override_soa_minimum(self):
        zone = Zone.objects.create(name="zone1.example.com", soa_minimum=42)

        self.assertEqual(zone.soa_minimum, 42)

    def test_default_soa_serial_auto(self):
        zone = Zone.objects.create(name="zone1.example.com")

        self.assertTrue(zone.soa_serial_auto)

    def test_override_soa_serial(self):
        zone = Zone.objects.create(
            name="zone1.example.com", soa_serial_auto=False, soa_serial=42
        )

        self.assertEqual(zone.soa_serial, 42)

    def test_override_soa_rname(self):
        zone = Zone.objects.create(
            name="zone1.example.com", soa_rname="postmaster.example.com"
        )

        self.assertEqual(zone.soa_rname, "postmaster.example.com")

    def test_override_soa_mname(self):
        nameserver = NameServer.objects.create(name="ns2.example.com")

        zone = Zone.objects.create(name="zone1.example.com", soa_mname=nameserver)

        self.assertEqual(zone.soa_mname, nameserver)

    def test_missing_soa_rname(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        del test_settings["zone_soa_rname"]

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            with self.assertRaises(ValidationError):
                Zone.objects.create(name="zone1.example.com")

    def test_missing_soa_mname(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        del test_settings["zone_soa_mname"]

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            with self.assertRaises(ValidationError):
                Zone.objects.create(name="zone1.example.com")

    def test_invalid_soa_mname(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        test_settings["zone_soa_mname"] = "nonexistent.example.com"

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            with self.assertRaises(ValidationError):
                Zone.objects.create(name="zone1.example.com")

    def test_override_invalid_soa_mname(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        test_settings["zone_soa_mname"] = "nonexistent.example.com"

        nameserver = NameServer.objects.create(name="ns2.example.com")

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            Zone.objects.create(name="zone1.example.com", soa_mname=nameserver)
