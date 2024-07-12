from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone, Record
from netbox_dns.choices import RecordTypeChoices


class RecordEnforceUniqueTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.record_data = {"type": RecordTypeChoices.AAAA, "value": "fe80:dead:beef::"}

        cls.zone = Zone.objects.create(name="zone1.example.com", **zone_data)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_unique_records_ok(self):
        records = (
            Record(name="name1", zone=self.zone, **self.record_data),
            Record(name="name2", zone=self.zone, **self.record_data),
            Record(name="name3", zone=self.zone, **self.record_data),
            Record(name="name4", zone=self.zone, **self.record_data),
        )

        for record in records:
            record.save()

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_duplicate_record_fail(self):
        Record.objects.create(name="name1", zone=self.zone, **self.record_data)

        with self.assertRaises(ValidationError):
            Record.objects.create(name="name1", zone=self.zone, **self.record_data)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_save_record_ok(self):
        Record.objects.create(name="name1", zone=self.zone, **self.record_data)
