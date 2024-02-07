from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import Zone, Record, RecordTypeChoices, NameServer


class RecordValidationTest(TestCase):
    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
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

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": False,
            }
        }
    )
    def test_create_unique_records(self):
        f_zone = self.zones[0]

        records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
            {"name": "test2", "type": RecordTypeChoices.A, "value": "10.0.2.42"},
        ]

        for record in records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            f_record.save()

    def test_create_duplicate_records_ok(self):
        f_zone = self.zones[0]

        records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
        ]

        for record in records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            f_record.save()

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_create_different_type_records_ok(self):
        f_zone = self.zones[0]

        records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
            {"name": "test1", "type": RecordTypeChoices.TXT, "value": "10.0.1.42"},
        ]

        for record in records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            f_record.save()

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_create_duplicate_records_fail(self):
        f_zone = self.zones[0]

        records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
        ]

        duplicate_records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
        ]

        for record in records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            f_record.save()

        for record in duplicate_records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            with self.assertRaises(ValidationError):
                f_record.save()
