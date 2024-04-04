from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import Zone, Record, RecordTypeChoices, NameServer


class RecordNormalizationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.zone = Zone.objects.create(name="zone1.example.com", **zone_data)

    def test_normalize_to_empty_name(self):
        record = Record.objects.create(
            name="zone1.example.com.",
            zone=self.zone,
            type=RecordTypeChoices.A,
            value="10.0.1.42",
        )

        self.assertEqual(record.name, "@")

    def test_normalize_to_relative_name(self):
        record = Record.objects.create(
            name="sub.zone1.example.com.",
            zone=self.zone,
            type=RecordTypeChoices.A,
            value="10.0.1.42",
        )

        self.assertEqual(record.name, "sub")

    def test_normalize_to_empty_name_nonmatching_zone(self):
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="zone2.example.com.",
                zone=self.zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_relative_name_nonmatching_zone(self):
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="sub.zone2.example.com.",
                zone=self.zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_empty_name_parent_zone(self):
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="example.com.",
                zone=self.zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )

    def test_normalize_to_relative_name_parent_zone(self):
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="example.com.",
                zone=self.zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            )
