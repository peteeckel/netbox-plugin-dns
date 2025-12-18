from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import Zone, Record, NameServer
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


class RecordUniquenessTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.zones = [
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="1.0.10.in-addr.arpa", **zone_data),
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
        zone = self.zones[0]

        records = (
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            ),
            Record(
                name="test2", zone=zone, type=RecordTypeChoices.A, value="10.0.2.42"
            ),
        )
        for record in records:
            record.save()

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {
                "enforce_unique_records": False,
            }
        }
    )
    def test_create_duplicate_records_ok(self):
        zone = self.zones[0]

        records = (
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            ),
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            ),
        )
        for record in records:
            record.save()

    def test_create_different_type_records_ok(self):
        zone = self.zones[0]

        records = (
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            ),
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.TXT, value="10.0.2.42"
            ),
        )
        for record in records:
            record.save()

    def test_create_duplicate_records_inactive_ok(self):
        zone = self.zones[0]

        records = (
            Record(
                name="test1",
                zone=zone,
                type=RecordTypeChoices.A,
                value="10.0.1.42",
                status=RecordStatusChoices.STATUS_INACTIVE,
            ),
            Record(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            ),
        )
        for record in records:
            record.save()

    def test_create_duplicate_records_fail(self):
        zone = self.zones[0]

        Record.objects.create(
            name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
        )
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="test1", zone=zone, type=RecordTypeChoices.A, value="10.0.1.42"
            )

    def test_rrset_ttl_new_record_ok(self):
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=86400,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)

    def test_rrset_ttl_create_record_fail(self):
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        with self.assertRaises(ValidationError):
            Record.objects.create(
                name="test1",
                zone=zone,
                type=RecordTypeChoices.A,
                value="10.0.1.2",
                ttl=43200,
            )

        self.assertEqual(record1.ttl, 86400)

    def test_rrset_ttl_create_record_without_ttl_set_ttl(self):
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=None,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)

    def test_rrset_ttl_create_record_inactive_ok(self):
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
            status=RecordStatusChoices.STATUS_INACTIVE,
        )
        record2 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.2",
            ttl=43200,
        )

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)

    def test_rrset_ttl_update_record(self):
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="test1",
            zone=zone,
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
        zone = self.zones[0]

        record1 = Record.objects.create(
            name="test1",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="test2",
            zone=zone,
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
        zone = self.zones[0]

        record1 = Record.objects.create(
            zone=zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=zone,
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
        zone = self.zones[0]

        record1 = Record.objects.create(
            zone=zone,
            name="test1",
            type=RecordTypeChoices.A,
            value="10.0.1.1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            zone=zone,
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
