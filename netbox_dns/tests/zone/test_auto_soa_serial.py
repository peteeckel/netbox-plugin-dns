from time import time
from datetime import datetime, timedelta
from math import ceil
from dns import rdata

from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import (
    NameServer,
    Record,
    RecordTypeChoices,
    RecordClassChoices,
    Zone,
)


def set_soa_serial_back(zone):
    zone.last_updated = datetime.now() - timedelta(days=1)
    zone.soa_serial = ceil(zone.last_updated.timestamp())
    super(Zone, zone).save()
    zone.update_soa_record()


def parse_soa_value(soa):
    return rdata.from_text(
        rdclass=RecordClassChoices.IN, rdtype=RecordTypeChoices.SOA, tok=soa
    )


class ZoneAutoSOASerialTestCase(TestCase):
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

    @classmethod
    def setUpTestData(cls):
        cls.start_time = int(time())

        cls.nameservers = (
            NameServer.objects.create(name="ns1.example.com"),
            NameServer.objects.create(name="ns2.example.com"),
        )

        cls.zones = (
            Zone(
                name="zone1.example.com",
                **cls.zone_data,
                soa_mname=cls.nameservers[0],
                soa_serial_auto=True,
            ),
            Zone(
                name="zone2.example.com",
                **cls.zone_data,
                soa_mname=cls.nameservers[0],
                soa_serial_auto=False,
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameservers[0],
                soa_serial_auto=True,
            ),
            Zone(
                name="2.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameservers[0],
                soa_serial_auto=False,
            ),
        )
        for zone in cls.zones:
            zone.save()

    def test_soa_serial_auto(self):
        zone = self.zones[0]
        zone.save()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_soa_serial_fixed(self):
        zone = self.zones[1]
        zone.save()

        self.assertEqual(zone.soa_serial, 1)

    def test_change_to_soa_serial_auto(self):
        zone = self.zones[1]
        zone.save()

        zone.soa_serial_auto = True
        zone.save()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_change_to_soa_serial_fixed(self):
        zone = self.zones[0]
        zone.save()

        zone.soa_serial_auto = False
        zone.soa_serial = 42
        zone.save()

        self.assertEqual(zone.soa_serial, 42)

    def modify_zone_soa_serial_auto(self):
        zone = self.zones[0]

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        zone.soa_rname = "admin.example.com"
        zone.save()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_missing_soa_serial(self):
        zone = self.zones[0]
        zone.soa_serial = None
        zone.soa_serial_auto = False

        with self.assertRaises(ValidationError):
            zone.save()

    def test_add_nameservers_soa_serial_auto(self):
        zone = self.zones[0]

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        zone.nameservers.add(self.nameservers[0])
        zone.nameservers.add(self.nameservers[1])

        self.assertTrue(int(zone.soa_serial) < self.start_time)

    def test_remove_nameservers_soa_serial_auto(self):
        zone = self.zones[0]

        zone.nameservers.add(self.nameservers[0])
        zone.nameservers.add(self.nameservers[1])

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        for nameserver in zone.nameservers.all():
            zone.nameservers.remove(nameserver)

        zone.refresh_from_db()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_create_record_soa_serial_auto(self):
        zone = self.zones[0]

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        record = Record(
            zone=zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        record.save()

        zone.refresh_from_db()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_update_record_soa_serial_auto(self):
        zone = self.zones[0]

        record = Record(
            zone=zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        record.save()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        record.ttl = 424242
        record.save()

        self.assertTrue(int(zone.soa_serial) >= self.start_time)

    def test_update_soa_record_soa_serial_auto(self):
        zone = self.zones[0]

        set_soa_serial_back(zone)

        self.assertTrue(int(zone.soa_serial) < self.start_time)

        soa_record = Record.objects.get(zone=zone, type=RecordTypeChoices.SOA)
        soa_record.ttl = 424242
        soa_record.save()

        zone.refresh_from_db()

        self.assertFalse(int(zone.soa_serial) >= self.start_time)

    def test_create_ptr_soa_serial_fixed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[3]

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.2.42",
            ttl=86400,
        )
        f_record.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR,
            value=f"{f_record.name}.{f_zone.name}.",
            zone=r_zone,
        )
        r_zone = Zone.objects.get(pk=r_record.zone.pk)

        self.assertEqual(r_zone.soa_serial, 1)

    def test_create_address_with_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)

        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)

    def test_delete_address_with_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        f_record.delete()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)

        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)

    def test_disable_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        f_record.disable_ptr = True
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)

        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)

    def test_enable_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
            disable_ptr=True,
        )
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()

        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)

        f_record.disable_ptr = False
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)

        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)

    def test_rfc2317_create_address_parent_managed_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        rfc2317_zone = Zone.objects.create(
            name="0-31.1.0.10.in-addr.arpa",
            **self.zone_data,
            soa_mname=self.nameservers[0],
            soa_serial_auto=True,
            rfc2317_prefix="10.0.1.0/26",
            rfc2317_parent_managed=True,
        )

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)
        set_soa_serial_back(rfc2317_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)
        rfc2317_soa_record = Record.objects.get(
            type=RecordTypeChoices.SOA, zone=rfc2317_zone
        )

        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)
        self.assertEqual(
            parse_soa_value(rfc2317_soa_record.value).serial, rfc2317_zone.soa_serial
        )

    def test_rfc2317_create_address_parent_unmanaged_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        rfc2317_zone = Zone.objects.create(
            name="0-31.1.0.10.in-addr.arpa",
            **self.zone_data,
            soa_mname=self.nameservers[0],
            soa_serial_auto=True,
            rfc2317_prefix="10.0.1.0/26",
            rfc2317_parent_managed=False,
        )

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)
        set_soa_serial_back(rfc2317_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)
        rfc2317_soa_record = Record.objects.get(
            type=RecordTypeChoices.SOA, zone=rfc2317_zone
        )

        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)
        self.assertEqual(
            parse_soa_value(rfc2317_soa_record.value).serial, rfc2317_zone.soa_serial
        )

    def test_rfc2317_set_parent_managed_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        rfc2317_zone = Zone.objects.create(
            name="0-31.1.0.10.in-addr.arpa",
            **self.zone_data,
            soa_mname=self.nameservers[0],
            soa_serial_auto=True,
            rfc2317_prefix="10.0.1.0/26",
            rfc2317_parent_managed=False,
        )

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)
        set_soa_serial_back(rfc2317_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        rfc2317_zone.rfc2317_parent_managed = True
        rfc2317_zone.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)
        rfc2317_soa_record = Record.objects.get(
            type=RecordTypeChoices.SOA, zone=rfc2317_zone
        )

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)
        self.assertEqual(
            parse_soa_value(rfc2317_soa_record.value).serial, rfc2317_zone.soa_serial
        )

    def test_rfc2317_set_parent_unmanaged_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        rfc2317_zone = Zone.objects.create(
            name="0-31.1.0.10.in-addr.arpa",
            **self.zone_data,
            soa_mname=self.nameservers[0],
            soa_serial_auto=True,
            rfc2317_prefix="10.0.1.0/26",
            rfc2317_parent_managed=True,
        )

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
        )
        f_record.save()

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)
        set_soa_serial_back(rfc2317_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        rfc2317_zone.rfc2317_parent_managed = False
        rfc2317_zone.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)
        rfc2317_soa_record = Record.objects.get(
            type=RecordTypeChoices.SOA, zone=rfc2317_zone
        )

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) >= self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)
        self.assertEqual(
            parse_soa_value(rfc2317_soa_record.value).serial, rfc2317_zone.soa_serial
        )

    def test_rfc2317_create_address_parent_managed_disable_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        rfc2317_zone = Zone.objects.create(
            name="0-31.1.0.10.in-addr.arpa",
            **self.zone_data,
            soa_mname=self.nameservers[0],
            soa_serial_auto=True,
            rfc2317_prefix="10.0.1.0/26",
            rfc2317_parent_managed=False,
        )

        set_soa_serial_back(f_zone)
        set_soa_serial_back(r_zone)
        set_soa_serial_back(rfc2317_zone)

        self.assertTrue(int(f_zone.soa_serial) < self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        f_record = Record(
            zone=f_zone,
            name="name1",
            type=RecordTypeChoices.A,
            value="10.0.1.42",
            ttl=86400,
            disable_ptr=True,
        )
        f_record.save()

        f_zone.refresh_from_db()
        r_zone.refresh_from_db()
        rfc2317_zone.refresh_from_db()

        f_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=f_zone)
        r_soa_record = Record.objects.get(type=RecordTypeChoices.SOA, zone=r_zone)
        rfc2317_soa_record = Record.objects.get(
            type=RecordTypeChoices.SOA, zone=rfc2317_zone
        )

        self.assertTrue(int(f_zone.soa_serial) >= self.start_time)
        self.assertTrue(int(r_zone.soa_serial) < self.start_time)
        self.assertTrue(int(rfc2317_zone.soa_serial) < self.start_time)

        self.assertEqual(parse_soa_value(f_soa_record.value).serial, f_zone.soa_serial)
        self.assertEqual(parse_soa_value(r_soa_record.value).serial, r_zone.soa_serial)
        self.assertEqual(
            parse_soa_value(rfc2317_soa_record.value).serial, rfc2317_zone.soa_serial
        )
