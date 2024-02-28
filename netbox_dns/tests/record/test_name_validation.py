from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone, Record, RecordTypeChoices


class NameValidationTest(TestCase):
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

    record_data = {
        "type": RecordTypeChoices.AAAA,
        "value": "fe80:dead:beef::",
    }

    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zones = (
            Zone(**cls.zone_data, soa_mname=cls.nameserver, name="zone1.example.com"),
            Zone(**cls.zone_data, soa_mname=cls.nameserver, name="zone2.example.com."),
            Zone(
                **cls.zone_data,
                soa_mname=cls.nameserver,
                name="zone240" + 22 * ".123456789" + ".example.com",
            ),
            Zone(
                **cls.zone_data,
                soa_mname=cls.nameserver,
                name="zone240" + 22 * ".987654321" + ".example.com.",
            ),
            Zone(
                **cls.zone_data,
                soa_mname=cls.nameserver,
                name="f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
            ),
        )
        Zone.objects.bulk_create(cls.zones)
        for zone in cls.zones:
            zone.save()

    def test_name_validation_ok(self):
        records = (
            {"name": "*", "zone": self.zones[0]},
            {"name": "name1", "zone": self.zones[0]},
            {"name": "@", "zone": self.zones[0]},
            {"name": "*", "zone": self.zones[0]},
            {"name": "*.sub", "zone": self.zones[0]},
            {"name": "*.sub.zone1.example.com", "zone": self.zones[0]},
            {"name": "*.sub.zone1.example.com.", "zone": self.zones[0]},
            {"name": "name1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "name1", "zone": self.zones[1]},
            {"name": "@", "zone": self.zones[2]},
            {"name": "*", "zone": self.zones[2]},
            {"name": "name1.zone2.example.com.", "zone": self.zones[1]},
            {"name": "name-1", "zone": self.zones[0]},
            {"name": "name-1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "name-1", "zone": self.zones[1]},
            {"name": "name-1.zone2.example.com.", "zone": self.zones[1]},
            {"name": "x" * 13, "zone": self.zones[2]},
            {"name": "x" * 13, "zone": self.zones[3]},
            {"name": "x" * 63 + f".{self.zones[0].name}.", "zone": self.zones[0]},
            {"name": "x" * 63 + f".{self.zones[1].name}", "zone": self.zones[1]},
            {"name": "xn--nme1-loa", "zone": self.zones[0]},
            {"name": "xn--nme1-loa.zone1.example.com.", "zone": self.zones[0]},
            {"name": "XN--nme1-loa", "zone": self.zones[0]},
            {"name": "XN--nme1-loa.zone1.example.com.", "zone": self.zones[0]},
        )

        for record in records:
            record_object = Record.objects.create(
                name=record.get("name"), zone=record.get("zone"), **self.record_data
            )

    def test_srv_validation_ok(self):
        record = Record.objects.create(
            name="_ldaps._tcp",
            zone=self.zones[0],
            type=RecordTypeChoices.SRV,
            value="10 5 636 server.example.com.",
        )
        self.assertEqual(record.name, "_ldaps._tcp")

    def test_txt_validation_ok(self):
        record = Record.objects.create(
            name="_dmarc",
            zone=self.zones[0],
            type=RecordTypeChoices.TXT,
            value="v=DMARC1;p=reject",
        )
        self.assertEqual(record.name, "_dmarc")

    def test_name_validation_failure(self):
        records = (
            {"name": "_name1", "zone": self.zones[0]},
            {"name": "name1..", "zone": self.zones[0]},
            {"name": "@.", "zone": self.zones[0]},
            {"name": "*.", "zone": self.zones[0]},
            {"name": "*.sub.", "zone": self.zones[0]},
            {"name": "*.*", "zone": self.zones[0]},
            {"name": "*.*.", "zone": self.zones[0]},
            {"name": "name1.zone2.example.com.", "zone": self.zones[0]},
            {"name": "name1.zone1.example.com.", "zone": self.zones[1]},
            {"name": "name_1", "zone": self.zones[0]},
            {"name": "name_1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "-name1", "zone": self.zones[0]},
            {"name": "-name1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "name1-", "zone": self.zones[0]},
            {"name": "name1-.zone1.example.com.", "zone": self.zones[0]},
            {"name": "na--me1", "zone": self.zones[0]},
            {"name": "na--me1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "x" * 14, "zone": self.zones[2]},
            {"name": "x" * 14, "zone": self.zones[3]},
            {"name": "\\000" * 14, "zone": self.zones[2]},
            {"name": "\\000" * 14, "zone": self.zones[3]},
            {"name": "x" * 64 + f".{self.zones[0].name}.", "zone": self.zones[0]},
            {"name": "x" * 64 + f".{self.zones[1].name}", "zone": self.zones[1]},
            {"name": "xn--n", "zone": self.zones[0]},
            {"name": "xn--n.zone1.example.com.", "zone": self.zones[0]},
        )

        for record in records:
            with self.assertRaises(ValidationError):
                Record.objects.create(
                    name=record.get("name"), zone=record.get("zone"), **self.record_data
                )

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
                "tolerate_leading_underscore_types": ["TXT", "SRV"],
                "tolerate_non_rfc1035_types": [],
            }
        }
    )
    def test_name_validation_tolerant_ok(self):
        records = (
            {"name": "name_1", "zone": self.zones[0]},
            {"name": "name_1.zone1.example.com.", "zone": self.zones[0]},
        )

        for record in records:
            record_object = Record.objects.create(
                name=record.get("name"), zone=record.get("zone"), **self.record_data
            )

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
                "tolerate_leading_underscore_types": ["TXT", "SRV"],
                "tolerate_non_rfc1035_types": [],
            }
        }
    )
    def test_srv_validation_tolerant_ok(self):
        record = Record.objects.create(
            name="_ldaps._tcp",
            zone=self.zones[0],
            type=RecordTypeChoices.SRV,
            value="10 5 636 server.example.com.",
        )
        self.assertEqual(record.name, "_ldaps._tcp")

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
                "tolerate_leading_underscore_types": ["TXT", "SRV"],
                "tolerate_non_rfc1035_types": [],
            }
        }
    )
    def test_txt_validation_tolerant_ok(self):
        records = (
            {
                "name": "_dmarc",
                "zone": self.zones[0],
                "type": RecordTypeChoices.TXT,
                "value": "v=DMARC1;p=reject",
            },
            {
                "name": "key1_op16._domainkey",
                "zone": self.zones[0],
                "type": RecordTypeChoices.TXT,
                "value": "test",
            },
        )
        for record in records:
            record_object = Record.objects.create(**record)
            self.assertEqual(record_object.name, record.get("name"))

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "tolerate_underscores_in_hostnames": True,
                "tolerate_leading_underscore_types": ["TXT", "SRV"],
                "tolerate_non_rfc1035_types": [],
            }
        }
    )
    def test_name_validation_tolerant_failure(self):
        records = (
            {"name": "_name1", "zone": self.zones[0]},
            {"name": "_name1.zone1.example.com.", "zone": self.zones[0]},
            {"name": "name1_", "zone": self.zones[0]},
            {"name": "name1_.zone1.example.com.", "zone": self.zones[0]},
        )

        for record in records:
            with self.assertRaises(ValidationError):
                Record.objects.create(
                    name=record.get("name"), zone=record.get("zone"), **self.record_data
                )
