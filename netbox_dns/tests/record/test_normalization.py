from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import Zone, Record, RecordTypeChoices, NameServer


class RecordNormalizationTestCase(TestCase):
    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 43200,
        "soa_retry": 7200,
        "soa_expire": 2419200,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial": 1,
    }

    record_data = {
        "ttl": 86400,
    }

    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")
        cls.zones = [
            Zone(name="zone1.example.com", **cls.zone_data, soa_mname=cls.nameserver),
        ]
        Zone.objects.bulk_create(cls.zones)

    def test_normalize_to_empty_name(self):
        f_zone = self.zones[0]

        record = Record.objects.create(
            name="zone1.example.com.",
            zone=f_zone,
            type=RecordTypeChoices.A,
            value="10.0.1.42",
        )

        self.assertEqual(record.name, "@")

    def test_normalize_to_relative_name(self):
        f_zone = self.zones[0]

        record = Record.objects.create(
            name="sub.zone1.example.com.",
            zone=f_zone,
            type=RecordTypeChoices.A,
            value="10.0.1.42",
        )

        self.assertEqual(record.name, "sub")

    def test_normalize_to_empty_name_nonmatching_zone(self):
        f_zone = self.zones[0]

        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="zone2.example.com.",
                zone=f_zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_relative_name_nonmatching_zone(self):
        f_zone = self.zones[0]

        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="sub.zone2.example.com.",
                zone=f_zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_empty_name_parent_zone(self):
        f_zone = self.zones[0]

        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="example.com.",
                zone=f_zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_relative_name_parent_zone(self):
        f_zone = self.zones[0]

        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="example.com.",
                zone=f_zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )
