from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, View, Zone, Record, RecordTypeChoices


class RFC2317RecordTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zone_data = {
            "default_ttl": 86400,
            "soa_mname": cls.nameserver,
            "soa_rname": "hostmaster.example.com",
            "soa_refresh": 172800,
            "soa_retry": 7200,
            "soa_expire": 2592000,
            "soa_ttl": 86400,
            "soa_minimum": 3600,
            "soa_serial": 1,
            "soa_serial_auto": False,
        }

        cls.views = (
            View(name="internal"),
            View(name="external"),
        )
        View.objects.bulk_create(cls.views)

        cls.zones = (
            Zone(name="zone1.example.com", **cls.zone_data),
            Zone(name="zone2.example.com", **cls.zone_data),
            Zone(name="zone3.example.com", **cls.zone_data),
            Zone(name="zone1.example.com", **cls.zone_data, view=cls.views[0]),
            Zone(name="zone1.example.com", **cls.zone_data, view=cls.views[1]),
        )
        Zone.objects.bulk_create(cls.zones)

    def test_create_record_rfc2317_zone(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).count(), 3
        )
        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_disable_ptr(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                disable_ptr=True,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
                disable_ptr=True,
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
                disable_ptr=True,
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)

    def test_create_record_rfc2317_zone_view(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            view=self.views[1],
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_no_view(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name1",
                zone=self.zones[4],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_same_view(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            view=self.views[0],
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).count(), 2
        )
        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_different_prefices(self):
        rfc2317_zone1 = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )
        rfc2317_zone2 = Zone.objects.create(
            name="16-31.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.16/28",
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name3",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.21",
            ),
            Record(
                name="name4",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.22",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone1.record_set.filter(type=RecordTypeChoices.PTR).count(), 2
        )
        for record in records[0:2]:
            self.assertIn(record.ptr_record, rfc2317_zone1.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone1)
            self.assertTrue(
                rfc2317_zone1.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
        for record in records[2:4]:
            self.assertIn(record.ptr_record, rfc2317_zone2.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone2)
            self.assertTrue(
                rfc2317_zone2.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )

    def test_modify_record_rfc2317_zone_value_different_zone(self):
        rfc2317_zone1 = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )
        rfc2317_zone2 = Zone.objects.create(
            name="16-31.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.16/28",
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(record.ptr_record, rfc2317_zone1.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone1)
        self.assertTrue(
            rfc2317_zone1.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )

        record.value = "10.0.0.16"
        record.save()

        rfc2317_zone1.refresh_from_db()
        rfc2317_zone2.refresh_from_db()

        self.assertNotIn(record.ptr_record, rfc2317_zone1.record_set.all())
        self.assertNotEqual(record.ptr_record.zone, rfc2317_zone1)
        self.assertFalse(
            rfc2317_zone1.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertIn(record.ptr_record, rfc2317_zone2.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone2)
        self.assertTrue(
            rfc2317_zone2.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )

    def test_delete_record_rfc2317_zone(self):
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )

        record_pk = record.pk
        record.delete()

        rfc2317_zone.refresh_from_db()

        self.assertFalse(rfc2317_zone.record_set.filter(pk=record_pk).exists())
        self.assertFalse(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )

    def test_create_record_rfc2317_zone_managed(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).count(), 3
        )
        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_managed_disable_ptr(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                disable_ptr=True,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
                disable_ptr=True,
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
                disable_ptr=True,
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR, name=record.rfc2317_ptr_name
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME, name=record.rfc2317_ptr_cname_name
                ).exists()
            )

    def test_create_record_rfc2317_zone_managed_view(self):
        zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", view=self.views[1], **self.zone_data
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            view=self.views[1],
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name1",
                zone=self.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.3",
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR, name=record.rfc2317_ptr_name
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME, name=record.rfc2317_ptr_cname_name
                ).exists()
            )

    def test_create_record_rfc2317_zone_managed_no_view(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        )
        for record in records:
            record.save()

        self.assertFalse(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).exists()
        )
        for record in records:
            self.assertIsNone(record.ptr_record)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR, name=record.rfc2317_ptr_name
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME, name=record.rfc2317_ptr_cname_name
                ).exists()
            )

    def test_create_record_rfc2317_zone_managed_same_view(self):
        zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa", view=self.views[0], **self.zone_data
        )
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            view=self.views[0],
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[3],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone.record_set.filter(type=RecordTypeChoices.PTR).count(), 2
        )
        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_create_record_rfc2317_zone_managed_different_prefices(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone1 = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )
        rfc2317_zone2 = Zone.objects.create(
            name="16-31.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.16/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name3",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name4",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name5",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.21",
            ),
            Record(
                name="name6",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.22",
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            rfc2317_zone1.record_set.filter(type=RecordTypeChoices.PTR).count(), 4
        )
        for record in records[0:4]:
            self.assertIn(record.ptr_record, rfc2317_zone1.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone1)
            self.assertTrue(
                rfc2317_zone1.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )
        for record in records[4:6]:
            self.assertIn(record.ptr_record, rfc2317_zone2.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone2)
            self.assertTrue(
                rfc2317_zone2.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_modify_rfc2317_zone_managed_different_prefices(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="16-31.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name3",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name4",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        )
        for record in records:
            record.save()

        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

        rfc2317_zone.rfc2317_prefix = "10.0.0.16/28"
        rfc2317_zone.save()

        for record in records:
            record.refresh_from_db()
            self.assertNotIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertNotEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertFalse(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_modify_record_rfc2317_zone_managed_new_value_same_zone(self):
        zone = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record.ptr_record.fqdn, f"{record.rfc2317_ptr_name}.{rfc2317_zone.name}."
        )

        record.value = "10.0.0.2"
        record.save()

        rfc2317_zone.refresh_from_db()
        zone.refresh_from_db()

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record.ptr_record.fqdn, f"{record.rfc2317_ptr_name}.{rfc2317_zone.name}."
        )

    def test_modify_record_rfc2317_zone_managed_existing_value(self):
        zone = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record1 = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )
        record2 = Record.objects.create(
            name="name2", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.2"
        )

        self.assertIn(record1.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record1.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record1.rfc2317_ptr_name,
                value=record1.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record1.rfc2317_ptr_cname_name,
                value=record1.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record1.ptr_record.fqdn, f"{record1.rfc2317_ptr_name}.{rfc2317_zone.name}."
        )

        record1.value = "10.0.0.2"
        record1.save()

        rfc2317_zone.refresh_from_db()
        zone.refresh_from_db()

        self.assertIn(record1.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record1.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record1.rfc2317_ptr_name,
                value=record1.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record1.rfc2317_ptr_cname_name,
                value=record1.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record1.ptr_record.fqdn, f"{record1.rfc2317_ptr_name}.{rfc2317_zone.name}."
        )

    def test_delete_record_rfc2317_zone_managed(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

        record_pk = record.pk
        record.delete()

        zone1.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        self.assertFalse(rfc2317_zone.record_set.filter(pk=record_pk).exists())
        self.assertFalse(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR, name=record.rfc2317_ptr_name
            ).exists()
        )
        self.assertFalse(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME, name=record.rfc2317_ptr_cname_name
            ).exists()
        )

    def test_record_rfc2317_zone_set_unmanaged(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = [
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name3",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name4",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        ]
        for record in records:
            record.save()

        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        for record in records:
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

        rfc2317_zone.rfc2317_parent_managed = False
        rfc2317_zone.save()

        zone1.refresh_from_db()

        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertFalse(zone1.rfc2317_child_zones.exists())
        for record in records:
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_record_rfc2317_zone_set_managed(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
        )

        records = [
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name3",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
            Record(
                name="name4",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.2",
            ),
        ]
        for record in records:
            record.save()

        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertFalse(zone1.rfc2317_child_zones.exists())
        for record in records:
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertFalse(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

        rfc2317_zone.rfc2317_parent_managed = True
        rfc2317_zone.save()

        rfc2317_zone.refresh_from_db()
        zone1.refresh_from_db()

        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
        for record in records:
            record.refresh_from_db()

            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_record_delete_rfc2317_zone(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = [
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
        ]
        for record in records:
            record.save()

        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

        rfc2317_zone.delete()
        for record in records:
            record.refresh_from_db()

        self.assertFalse(zone1.rfc2317_child_zones.exists())
        for record in records:
            self.assertIn(record.ptr_record, zone1.record_set.all())
            self.assertEqual(record.ptr_record.zone, zone1)
            self.assertEqual(record.ptr_record.rfc2317_cname_record, None)
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.PTR, name="1", value=record.fqdn
                ).exists()
            )

    def test_record_create_rfc2317_zone(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)

        records = [
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            ),
        ]
        for record in records:
            record.save()

        self.assertFalse(zone1.rfc2317_child_zones.exists())
        for record in records:
            self.assertIn(record.ptr_record, zone1.record_set.all())
            self.assertEqual(record.ptr_record.zone, zone1)
            self.assertEqual(record.ptr_record.rfc2317_cname_record, None)
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.PTR, name="1", value=record.fqdn
                ).exists()
            )

        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )
        for record in records:
            record.refresh_from_db()

        for record in records:
            self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
            self.assertEqual(record.ptr_record.zone, rfc2317_zone)
            self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
            self.assertTrue(
                rfc2317_zone.record_set.filter(
                    type=RecordTypeChoices.PTR,
                    name=record.rfc2317_ptr_name,
                    value=record.fqdn,
                ).exists()
            )
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_record_delete_parent_zone(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        zone1_pk = zone1.pk

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

        zone1.delete()
        rfc2317_zone.refresh_from_db()
        record.refresh_from_db()

        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertFalse(Zone.objects.filter(pk=zone1_pk).exists())
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertIsNone(record.ptr_record.rfc2317_cname_record)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )

    def test_record_delete_parent_zone_new_parent(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = Zone.objects.create(name="0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        zone1_pk = zone1.pk

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

        zone1.delete()
        zone2.refresh_from_db()
        rfc2317_zone.refresh_from_db()
        record.refresh_from_db()

        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertFalse(Zone.objects.filter(pk=zone1_pk).exists())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone2.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

    def test_record_create_parent_zone_new_parent(self):
        zone1 = Zone.objects.create(name="0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(record.ptr_record, rfc2317_zone.record_set.all())
        self.assertEqual(record.ptr_record.zone, rfc2317_zone)
        self.assertEqual(record.ptr_record.rfc2317_cname_record.zone, zone1)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

        zone2 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone1.refresh_from_db()
        rfc2317_zone.refresh_from_db()
        record.refresh_from_db()

        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone2)
        self.assertTrue(
            rfc2317_zone.record_set.filter(
                type=RecordTypeChoices.PTR,
                name=record.rfc2317_ptr_name,
                value=record.fqdn,
            ).exists()
        )
        self.assertTrue(
            zone2.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )

    def test_set_zone_parent_managed_create_cname(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = self.zones[2]
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=False,
        )
        address_record = Record.objects.create(
            name="name1",
            zone=zone2,
            type=RecordTypeChoices.A,
            value="10.0.0.1",
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertNotIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertIsNotNone(address_record.ptr_record)
        self.assertEqual(address_record.ptr_record.zone, rfc2317_zone)
        self.assertIsNone(address_record.ptr_record.rfc2317_cname_record)

        cname_record = Record.objects.filter(
            zone=zone1,
            type=RecordTypeChoices.CNAME,
            managed=True,
            name="1",
        ).first()
        self.assertIsNone(cname_record)

        rfc2317_zone.rfc2317_parent_managed = True
        rfc2317_zone.save()
        address_record.refresh_from_db()

        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIsNotNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertIsNotNone(address_record.ptr_record.rfc2317_cname_record)

        cname_record = Record.objects.filter(
            zone=zone1,
            type=RecordTypeChoices.CNAME,
            managed=True,
            name="1",
        ).first()
        self.assertEqual(address_record.ptr_record.rfc2317_cname_record, cname_record)

    def test_set_zone_parent_unmanaged_delete_cname(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        zone2 = self.zones[2]
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )
        address_record = Record.objects.create(
            name="name1",
            zone=zone2,
            type=RecordTypeChoices.A,
            value="10.0.0.1",
        )

        self.assertIsNotNone(rfc2317_zone.pk)
        self.assertTrue(rfc2317_zone.rfc2317_parent_managed)
        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIsNotNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertIsNotNone(address_record.ptr_record)
        self.assertEqual(address_record.ptr_record.zone, rfc2317_zone)
        self.assertIsNotNone(address_record.ptr_record.rfc2317_cname_record)

        cname_record = Record.objects.filter(
            zone=zone1,
            type=RecordTypeChoices.CNAME,
            managed=True,
            name="1",
        ).first()
        self.assertEqual(address_record.ptr_record.rfc2317_cname_record, cname_record)

        rfc2317_zone.rfc2317_parent_managed = False
        rfc2317_zone.save()
        address_record.refresh_from_db()

        self.assertFalse(rfc2317_zone.rfc2317_parent_managed)
        self.assertNotIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertIsNone(address_record.ptr_record.rfc2317_cname_record)

        cname_record = Record.objects.filter(
            zone=zone1,
            type=RecordTypeChoices.CNAME,
            managed=True,
            name="1",
        ).first()
        self.assertIsNone(cname_record)

    def test_cname_ttl(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=86400,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=43200,
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            records[0].ptr_record.rfc2317_cname_record.pk,
            records[1].ptr_record.rfc2317_cname_record.pk,
        )

        self.assertEqual(records[0].ttl, 86400)
        self.assertEqual(records[0].ptr_record.ttl, 86400)
        self.assertEqual(records[1].ttl, 43200)
        self.assertEqual(records[1].ptr_record.ttl, 43200)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 43200)

    def test_cname_ttl_update_record_ttl(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=86400,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=43200,
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            records[0].ptr_record.rfc2317_cname_record.pk,
            records[1].ptr_record.rfc2317_cname_record.pk,
        )

        self.assertEqual(records[0].ttl, 86400)
        self.assertEqual(records[0].ptr_record.ttl, 86400)
        self.assertEqual(records[1].ttl, 43200)
        self.assertEqual(records[1].ptr_record.ttl, 43200)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 43200)

        records[1].ttl = 86400
        records[1].save()

        self.assertEqual(records[1].ttl, 86400)
        self.assertEqual(records[1].ptr_record.ttl, 86400)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 86400)

        records[0].ttl = 43200
        records[0].save()

        self.assertEqual(records[0].ttl, 43200)
        self.assertEqual(records[0].ptr_record.ttl, 43200)
        self.assertEqual(records[0].ptr_record.rfc2317_cname_record.ttl, 43200)

    def test_cname_ttl_set_record_ttl_none(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=86400,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=43200,
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            records[0].ptr_record.rfc2317_cname_record.pk,
            records[1].ptr_record.rfc2317_cname_record.pk,
        )

        self.assertEqual(records[0].ttl, 86400)
        self.assertEqual(records[0].ptr_record.ttl, 86400)
        self.assertEqual(records[1].ttl, 43200)
        self.assertEqual(records[1].ptr_record.ttl, 43200)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 43200)

        records[1].ttl = None
        records[1].save()

        self.assertEqual(records[1].ttl, None)
        self.assertEqual(records[1].ptr_record.ttl, None)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 86400)

        records[0].ttl = None
        records[0].save()

        self.assertEqual(records[0].ttl, None)
        self.assertEqual(records[0].ptr_record.ttl, None)
        self.assertEqual(records[0].ptr_record.rfc2317_cname_record.ttl, None)

    def test_cname_ttl_delete_record(self):
        zone1 = Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        rfc2317_zone = Zone.objects.create(
            name="0-15.0.0.10.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="10.0.0.0/28",
            rfc2317_parent_managed=True,
        )

        records = (
            Record(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=86400,
            ),
            Record(
                name="name2",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                ttl=43200,
            ),
        )
        for record in records:
            record.save()

        self.assertEqual(
            records[0].ptr_record.rfc2317_cname_record.pk,
            records[1].ptr_record.rfc2317_cname_record.pk,
        )

        self.assertEqual(records[0].ttl, 86400)
        self.assertEqual(records[0].ptr_record.ttl, 86400)
        self.assertEqual(records[1].ttl, 43200)
        self.assertEqual(records[1].ptr_record.ttl, 43200)
        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 43200)

        records[1].delete()
        records[0].ptr_record.refresh_from_db()

        self.assertEqual(records[1].ptr_record.rfc2317_cname_record.ttl, 86400)
