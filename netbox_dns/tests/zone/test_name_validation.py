from django.conf import settings
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone


class ZoneNameValidationTestCase(TestCase):
    zone_defaults = settings.PLUGINS_CONFIG.get("netbox_dns")

    @classmethod
    def setUpTestData(cls):
        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

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
            zone = Zone.objects.create(name=name, **self.zone_data)
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
            "0/25.2.0.192.in-addr.arpa",  # RFC 2317 sample zone including "/"
            "10.0.0.42",  # Name is interpreted as IP address by inet_aton
            "0x2a",  # Name is interpreted as IP address by inet_aton
        )

        for name in names:
            with self.assertRaises(ValidationError):
                Zone.objects.create(name=name, **self.zone_data)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                **zone_defaults,
                "enable_root_zones": True,
            }
        }
    )
    def test_name_validation_ok_root_zone(self):
        zone = Zone.objects.create(name=".", **self.zone_data)
        self.assertEqual(zone.name, ".")

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                **zone_defaults,
                "tolerate_underscores_in_labels": True,
            }
        }
    )
    def test_name_validation_tolerant_ok(self):
        names = (
            "zone_1.example.com",  # underscore in first label
            "zone1.example_1.com",  # underscore in second label
        )

        for name in names:
            zone = Zone.objects.create(name=name, **self.zone_data)
            self.assertEqual(zone.name, name.rstrip("."))

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                **zone_defaults,
                "tolerate_underscores_in_labels": True,
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
                Zone.objects.create(name=name, **self.zone_data)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                **zone_defaults,
                "tolerate_characters_in_zone_labels": "/",
            }
        }
    )
    def test_name_validation_allow_special_character_ok(self):
        zone = Zone.objects.create(name="0/25.2.0.192.in-addr.arpa", **self.zone_data)

        self.assertEqual(zone.name, "0/25.2.0.192.in-addr.arpa")
