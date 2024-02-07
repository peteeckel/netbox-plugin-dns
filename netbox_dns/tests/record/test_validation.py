from django.test import TestCase
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
            Zone(name="1.0.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
        ]
        Zone.objects.bulk_create(cls.zones)

    def test_create_record_validation_ok(self):
        f_zone = self.zones[0]

        ok_records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "10.0.1.42"},
            {"name": "test2", "type": RecordTypeChoices.A, "value": "10.0.2.42"},
            {
                "name": "test3",
                "type": RecordTypeChoices.AAAA,
                "value": "fe80:dead:beef::1:42",
            },
            {
                "name": "test4",
                "type": RecordTypeChoices.AAAA,
                "value": "fe80:dead:beef::2:42",
            },
            {
                "name": "test5",
                "type": RecordTypeChoices.MX,
                "value": "10 mx1.example.com",
            },
            {
                "name": "test6",
                "type": RecordTypeChoices.MX,
                "value": "10 mx1.example.com.",
            },
            {
                "name": "test8",
                "type": RecordTypeChoices.CAA,
                "value": "1 issue example.org",
            },
            {"name": "test9", "type": RecordTypeChoices.CNAME, "value": "test1"},
        ]

        for record in ok_records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )
            f_record.save()

    def test_create_record_validation_fail(self):
        f_zone = self.zones[0]

        broken_records = [
            {"name": "test1", "type": RecordTypeChoices.A, "value": "1.1.1.1.1"},
            {"name": "test2", "type": RecordTypeChoices.A, "value": "1.1.1"},
            {"name": "test3", "type": RecordTypeChoices.A, "value": "1.1.1.256"},
            {
                "name": "test4",
                "type": RecordTypeChoices.A,
                "value": "fe80:dead:beef:1:42:1111:2222:3333:4444",
            },
            {
                "name": "test5",
                "type": RecordTypeChoices.A,
                "value": "fe80:dead:beef:1:42:1111:2222",
            },
            {
                "name": "test6",
                "type": RecordTypeChoices.A,
                "value": "fe80:dead:beer:1:42:1111:2222:3333",
            },
            {"name": "test7", "type": RecordTypeChoices.AAAA, "value": "1.1.1.1.1"},
            {"name": "test8", "type": RecordTypeChoices.AAAA, "value": "1.1.1"},
            {"name": "test9", "type": RecordTypeChoices.AAAA, "value": "1.1.1.256"},
            {
                "name": "test10",
                "type": RecordTypeChoices.AAAA,
                "value": "fe80:dead:beef:42:1111:2222:3333:4444:5555",
            },
            {
                "name": "test11",
                "type": RecordTypeChoices.AAAA,
                "value": "fe80:dead:beef:42:1111:2222:3333",
            },
            {
                "name": "test12",
                "type": RecordTypeChoices.AAAA,
                "value": "fe80:dead:beer:42:1111:2222:3333:4444",
            },
            {
                "name": "test13",
                "type": RecordTypeChoices.MX,
                "value": "1000000 mx1.example.com",
            },
            {
                "name": "test13",
                "type": RecordTypeChoices.MX,
                "value": "1000000 1.1.1.1",
            },
            {
                "name": "test14",
                "type": RecordTypeChoices.SOA,
                "value": "(ns1.example.com. hostmaster.example.com. 1651498477 172800 7200 2592000)",
            },
            {
                "name": "test15",
                "type": RecordTypeChoices.SOA,
                "value": "(ns1.example.com. 1651498477 172800 7200 2592000 3600)",
            },
            {
                "name": "test16",
                "type": RecordTypeChoices.SOA,
                "value": "(ns1.example.com. hostmaster.example.com. -1 172800 7200 2592000 3600)",
            },
            {
                "name": "test17",
                "type": RecordTypeChoices.SOA,
                "value": "(ns1.example.com. hostmaster.example.com. claptrap 172800 7200 2592000 3600)",
            },
            {"name": "test18", "type": RecordTypeChoices.CAA, "value": "1"},
            {"name": "test19", "type": RecordTypeChoices.CAA, "value": "issue"},
            {"name": "test20", "type": RecordTypeChoices.CAA, "value": "1 issue"},
            {
                "name": "test21",
                "type": RecordTypeChoices.CAA,
                "value": "1 issue example.org claptrap",
            },
            {
                "name": "test22",
                "type": RecordTypeChoices.CNAME,
                "value": "test1 claptrap",
            },
        ]

        for record in broken_records:
            f_record = Record(
                zone=f_zone,
                **record,
                **self.record_data,
            )

            with self.assertRaises(ValidationError):
                f_record.save()

    def test_name_and_cname(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )

        with self.assertRaises(ValidationError):
            f_record2.save()

    def test_nsec_and_cname(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.NSEC,
            value="test2.zone1.example.com. A MX RRSIG NSEC",
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )
        f_record2.save()

        self.assertEqual(Record.objects.filter(name=name1, zone=f_zone).count(), 2)

    def test_cname_and_name(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )

        with self.assertRaises(ValidationError):
            f_record2.save()

    def test_cname_and_nsec(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.NSEC,
            value="test2.zone1.example.com. A MX RRSIG NSEC",
            **self.record_data,
        )
        f_record2.save()

        self.assertEqual(Record.objects.filter(name=name1, zone=f_zone).count(), 2)

    def test_double_singletons(self):
        f_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        name3 = "test3"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name2,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name3,
            **self.record_data,
        )

        with self.assertRaises(ValidationError):
            f_record2.save()

    def test_inactive_name_and_active_cname(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
            status="inactive",
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )
        f_record2.save()

    def test_inactive_cname_and_active_name(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
            status="inactive",
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record2.save()

    def test_double_singletons_inactive_active(self):
        f_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        name3 = "test3"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name2,
            **self.record_data,
            status="inactive",
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name3,
            **self.record_data,
        )
        f_record2.save()

    def test_active_name_and_inactive_cname(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
            status="inactive",
        )
        f_record2.save()

    def test_active_cname_and_inactive_name(self):
        f_zone = self.zones[0]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.CNAME,
            value=name2,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
            status="inactive",
        )
        f_record2.save()

    def test_double_singletons_active_inactive(self):
        f_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        name3 = "test3"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name2,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.DNAME,
            value=name3,
            **self.record_data,
            status="inactive",
        )
        f_record2.save()

    def test_lowercase_type(self):
        f_zone1 = self.zones[0]
        r_zone1 = self.zones[1]
        r_zone2 = self.zones[2]

        records = [
            {"zone": f_zone1, "name": "name1", "type": "a", "value": "10.0.1.1"},
            {
                "zone": f_zone1,
                "name": "name2",
                "type": "aaaa",
                "value": "fe80:dead:beef:42::1",
            },
            {
                "zone": f_zone1,
                "name": "name3",
                "type": "aAaA",
                "value": "fe80:dead:beef:42::2",
            },
            {"zone": f_zone1, "name": "name4", "type": "cname", "value": "name101"},
            {
                "zone": r_zone1,
                "name": "3",
                "type": "pTr",
                "value": "name3.example.com.",
            },
            {
                "zone": r_zone2,
                "name": "1.0.0.0.2.4.0.0.0.0.0.0.0.0.0.0",
                "type": "ptr",
                "value": "name2.example.com.",
            },
        ]

        for record in records:
            f_record = Record(
                **record,
                **self.record_data,
            )
            f_record.save()

            test_record = Record.objects.get(zone=record["zone"], name=record["name"])
            self.assertEqual(test_record.type, record["type"].upper())
