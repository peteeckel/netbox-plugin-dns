from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import Zone, Record, RecordTypeChoices, NameServer


class RecordUniquenessTestCase(TestCase):
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
            Zone(name="1.0.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
        ]
        for zone in cls.zones:
            zone.save()

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

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": False,
            }
        }
    )
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

    def test_rrset_ttl_new_record_ok(self):
        record1 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=86400,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)

    def test_rrset_ttl_create_record_fail(self):
        Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        with self.assertRaises(ValidationError):
            Record.objects.create(
                zone=self.zones[0],
                name="test1",
                type=RecordTypeChoices.A,
                value="10.0.1.2",
                ttl=43200,
            )

    def test_rrset_ttl_update_record(self):
        record1 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=86400,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)

        record2.ttl = 43200
        record2.save()
        record1.refresh_from_db()

        self.assertEqual(record1.ttl, 43200)
        self.assertEqual(record2.ttl, 43200)

    def test_rrset_ttl_ptr_records(self):
        f_zone = self.zones[0]

        record1 = Record.objects.create(
            zone=f_zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=f_zone,
            name="test2",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=43200,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)
        self.assertEqual(record1.ptr_record.ttl, 86400)
        self.assertEqual(record2.ptr_record.ttl, 43200)

    def test_rrset_ttl_add_unmanaged_ptr_record(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        f_record = Record.objects.create(
            zone=f_zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )

        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)

        r_record = Record.objects.create(
            zone=r_zone,
            name="1",
            type=RecordTypeChoices.PTR,
            value="name1.zone1.example.com.",
            ttl=43200,
        )

        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)
        self.assertEqual(r_record.ttl, 43200)

    def test_rrset_ttl_add_managed_ptr_record(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        r_record = Record.objects.create(
            zone=r_zone,
            name="1",
            type=RecordTypeChoices.PTR,
            value="name1.zone1.example.com.",
            ttl=43200,
        )

        self.assertEqual(r_record.ttl, 43200)

        f_record = Record.objects.create(
            zone=f_zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )

        r_record.refresh_from_db()

        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)
        self.assertEqual(r_record.ttl, 43200)

    def test_rrset_ttl_update_unmanaged_ptr_record(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        f_record = Record.objects.create(
            zone=f_zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        r_record = Record.objects.create(
            zone=r_zone,
            name="1",
            type=RecordTypeChoices.PTR,
            value="name1.zone1.example.com.",
            ttl=86400,
        )

        self.assertEqual(r_record.ttl, 86400)
        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)

        r_record.ttl = 43200
        r_record.save()

        f_record.refresh_from_db()

        self.assertEqual(r_record.ttl, 43200)
        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)

    def test_rrset_ttl_update_managed_ptr_record(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        f_record = Record.objects.create(
            zone=f_zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=43200,
        )
        r_record = Record.objects.create(
            zone=r_zone,
            name="1",
            type=RecordTypeChoices.PTR,
            value="name1.zone1.example.com.",
            ttl=43200,
        )

        self.assertEqual(r_record.ttl, 43200)
        self.assertEqual(f_record.ttl, 43200)
        self.assertEqual(f_record.ptr_record.ttl, 43200)

        f_record.ttl = 86400
        f_record.save()

        r_record.refresh_from_db()

        self.assertEqual(r_record.ttl, 43200)
        self.assertEqual(f_record.ttl, 86400)
        self.assertEqual(f_record.ptr_record.ttl, 86400)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_rrset_ttl": False,
            }
        }
    )
    def test_rrset_ttl_create_record_unenforced_ok(self):
        record1 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=43200,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_rrset_ttl": False,
            }
        }
    )
    def test_rrset_ttl_update_record_unenforced(self):
        record1 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=self.zones[0],
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=86400,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)

        record2.ttl = 43200
        record2.save()
        record1.refresh_from_db()

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)
