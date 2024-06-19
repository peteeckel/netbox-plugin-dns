from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer


class NameServerNameValidationTestCase(TestCase):
    def test_name_validation_ok(self):
        names = (
            "ns1.example.com",
            "ns2.example.com.",
            "ns-1.example.com",  # dash in first label
            "ns1.example-1.com",  # dash in second label
            "123456" + ".12345678" * 26 + ".example1.com",  # 254 octets
            "123456" + ".12345678" * 26 + ".example2.com.",  # 255 octets, trailing dot
            "x" * 63 + ".example1.com",  # longest label 63 octets
            "x" * 63 + ".example2.com.",  # longest label 63 octets, trailing dot
        )

        for name in names:
            nameserver = NameServer.objects.create(name=name)
            self.assertEqual(nameserver.name, name.rstrip("."))

    def test_name_validation_failure(self):
        names = (
            "-ns1.example.com",  # leading dash in first label
            "ns1.-example.com",  # leading dash in second label
            "ns1..example.com",  # empty label
            "n/s1.example.com",  # illegal character in host name
            "ns.ex/ample.com",  # illegal character in domain name
            "x" * 64 + ".example.com",  # label too long
            "12345678" + ".12345678" * 26 + ".example.com",  # 255 octets
            "123456789" + ".12345678" * 26 + ".example.com",  # 256 octets, trailing dot
        )

        for name in names:
            with self.assertRaises(ValidationError):
                NameServer.objects.create(name=name)

    @override_settings(
        PLUGINS_CONFIG={"netbox_dns": {"tolerate_underscores_in_labels": True}}
    )
    def test_name_validation_tolerant_ok(self):
        names = (
            "ns1.example.com",
            "ns2.example.com.",
            "ns_1.example.com",  # underscore in first label
            "ns1.example_1.com",  # undercore in second label
            "123456" + ".12345678" * 26 + ".example1.com",  # 254 octets
            "123456" + ".12345678" * 26 + ".example2.com.",  # 255 octets, trailing dot
            "x" * 63 + ".example1.com",  # longest label 63 octets
            "x" * 63 + ".example2.com.",  # longest label 63 octets, trailing dot
        )

        for name in names:
            nameserver = NameServer.objects.create(name=name)
            self.assertEqual(nameserver.name, name.rstrip("."))

    def test_name_validation_tolerant_failure(self):
        names = (
            "_ns1.example.com",  # leading underscore in first label
            "ns1._example.com",  # leading underscore in second label
            "ns_1.example.com",  # underscore in first label
            "ns1..example.com",  # empty label
            "x" * 64 + ".example.com",  # label too long
            "12345678" + ".12345678" * 26 + ".example.com",  # 255 octets
            "123456789" + ".12345678" * 26 + ".example.com",  # 256 octets, trailing dot
        )

        for name in names:
            with self.assertRaises(ValidationError):
                NameServer.objects.create(name=name)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_characters_in_zone_labels": "/",
            }
        }
    )
    def test_name_validation_allow_special_character_ok(self):
        NameServer.objects.create(name="ns1.ex/ample.com")

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_characters_in_zone_labels": "/",
            }
        }
    )
    def test_name_validation_allow_special_character_failure(self):
        with self.assertRaises(ValidationError):
            NameServer.objects.create(name="n/s1.example.com")
