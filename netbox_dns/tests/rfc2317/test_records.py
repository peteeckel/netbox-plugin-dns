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
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
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
            self.assertTrue(
                zone1.record_set.filter(
                    type=RecordTypeChoices.CNAME,
                    name=record.rfc2317_ptr_cname_name,
                    value=record.ptr_record.fqdn,
                ).exists()
            )

    def test_modify_record_rfc2317_zone_managed_value_different_zone(self):
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
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record.ptr_record.fqdn, f"{record.rfc2317_ptr_name}.{rfc2317_zone1.name}."
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
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.CNAME,
                name=record.rfc2317_ptr_cname_name,
                value=record.ptr_record.fqdn,
            ).exists()
        )
        self.assertEqual(
            record.ptr_record.fqdn, f"{record.rfc2317_ptr_name}.{rfc2317_zone2.name}."
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

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
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

        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        self.assertIsNone(rfc2317_zone.rfc2317_parent_zone)
        self.assertFalse(zone1.rfc2317_child_zones.exists())
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
        record.refresh_from_db()

        self.assertIn(rfc2317_zone, zone1.rfc2317_child_zones.all())
        self.assertEqual(rfc2317_zone.rfc2317_parent_zone, zone1)
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

        rfc2317_zone.delete()
        record.refresh_from_db()

        self.assertFalse(zone1.rfc2317_child_zones.exists())
        self.assertIn(record.ptr_record, zone1.record_set.all())
        self.assertEqual(record.ptr_record.zone, zone1)
        self.assertEqual(record.ptr_record.rfc2317_cname_record, None)
        self.assertTrue(
            zone1.record_set.filter(
                type=RecordTypeChoices.PTR, name="1", value=record.fqdn
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
