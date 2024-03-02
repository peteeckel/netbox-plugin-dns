from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone, Record, RecordTypeChoices


class RecordEnforceUniqueTest(TestCase):
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
        cls.zone = Zone.objects.create(
            **cls.zone_data, soa_mname=cls.nameserver, name="zone1.example.com"
        )

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_unique_records_ok(self):
        records = (
            {"name": "name1", "zone": self.zone, **self.record_data},
            {"name": "name2", "zone": self.zone, **self.record_data},
            {"name": "name3", "zone": self.zone, **self.record_data},
            {"name": "name4", "zone": self.zone, **self.record_data},
        )

        for record in records:
            Record.objects.create(**record)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": True,
            }
        }
    )
    def test_duplicate_record_fail(self):
        record = Record.objects.create(name="name1", zone=self.zone, **self.record_data)

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
        record = Record.objects.create(name="name1", zone=self.zone, **self.record_data)

        record.save()
