from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone


class ZoneNameValidationTestCase(TestCase):
    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial": 1,
        "soa_serial_auto": False,
    }

    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

    def test_name_validation_ok(self):
        names = (
            "zone1.example.com",
            "zone2.example.com.",
            "xn--zne1-5qa.example.com",  # IDN in first label
            "zone1.xn--exmple-cua.com",  # IDN in second label
            "zone-1.example.com",  # dash in first label
            "zone1.example-1.com",  # dash in second label
            "123456" + ".12345678" * 26 + ".example1.com",  # 254 octets
            "123456" + ".12345678" * 26 + ".example2.com.",  # 255 octets, trailing dot
            "x" * 63 + ".example1.com",  # longest label 63 octets
            "x" * 63 + ".example2.com.",  # longest label 63 octets, trailing dot
            "0-32.10.10.10.in-addr.arpa",  # RFC2317 zone name
        )

        for name in names:
            zone = Zone.objects.create(
                name=name, **self.zone_data, soa_mname=self.nameserver
            )
            self.assertEqual(zone.name, name.rstrip("."))

    def test_name_validation_failure(self):
        names = (
            "-zone.example.com",  # leading dash in first label
            "zone1.-example.com",  # leading dash in second label
            "zone1-.example.com",  # trailing dash in first label
            "zone1.example-.com",  # trailing dash in second label
            "zo--ne1.example.com",  # dashes in position 3, 4 of first label
            "zone1.ex--ample.com",  # dashes in position 3, 4 of second label
            "xn--z.example.com",  # invalid IDN in first label
            "zone1.xn--e.com",  # invalid IDN in second label
            "zone1..example.com",  # empty label
            "-zone1..example.com-1",  # leading dash
            "x" * 64 + ".example.com",  # label too long
            "12345678" + ".12345678" * 26 + ".example.com",  # 255 octets
            "123456789"
            + ".12345678" * 26
            + ".example.com.",  # 256 octets, trailing dot
            ".",  # root zone
        )

        for name in names:
            with self.assertRaises(ValidationError):
                Zone.objects.create(
                    name=name, **self.zone_data, soa_mname=self.nameserver
                )

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enable_root_zones": True,
            }
        }
    )
    def test_name_validation_ok_root_zone(self):
        zone = Zone.objects.create(
            name=".", **self.zone_data, soa_mname=self.nameserver
        )
        self.assertEqual(zone.name, ".")

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
            }
        }
    )
    def test_name_validation_tolerant_ok(self):
        names = (
            "zone_1.example.com",  # underscore in first label
            "zone1.example_1.com",  # underscore in second label
        )

        for name in names:
            zone = Zone.objects.create(
                name=name, **self.zone_data, soa_mname=self.nameserver
            )
            self.assertEqual(zone.name, name.rstrip("."))

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
            }
        }
    )
    def test_name_validation_tolerant_failure(self):
        names = (
            "_zone1.example.com",  # leading underscore in first label
            "zone1._example.com",  # leading underscore in second label
            "zone1_.example.com",  # trailing underscore in first label
            "zone1.example_.com",  # trailing underscore in second label
            "zone1..example.com",  # empty label
            "x" * 64 + ".example.com",  # label too long
            "12345678" + ".12345678" * 26 + ".example.com",  # 255 octets
            "123456789" + ".12345678" * 26 + ".example.com",  # 256 octets, trailing dot
        )

        for name in names:
            with self.assertRaises(ValidationError):
                Zone.objects.create(
                    name=name, **self.zone_data, soa_mname=self.nameserver
                )
