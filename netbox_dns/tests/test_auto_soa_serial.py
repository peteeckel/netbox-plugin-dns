import re

from time import time
from math import ceil
from random import randint

from django.test import TestCase

from netbox_dns.models import NameServer, Zone, Record


class AutoSOASerialTest(TestCase):

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

        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zones = [
            Zone(
                name="zone1.example.com",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                soa_serial_auto=True,
            ),
            Zone(
                name="zone2.example.com",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                soa_serial_auto=False,
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                soa_serial_auto=True,
            ),
            Zone(
                name="2.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                soa_serial_auto=False,
            ),
        ]
        Zone.objects.bulk_create(cls.zones)

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

    def test_create_ptr_soa_serial_auto(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        f_record = Record(
            zone=f_zone, name="name1", type=Record.A, value="10.0.1.42", ttl=86400
        )
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, value=f"{f_record.name}.{f_zone.name}.", zone=r_zone
        )
        r_zone = Zone.objects.get(pk=r_record.zone.pk)

        self.assertTrue(int(r_zone.soa_serial) >= int(f_zone.soa_serial))

    def test_create_ptr_soa_serial_fixed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[3]

        f_record = Record(
            zone=f_zone, name="name1", type=Record.A, value="10.0.2.42", ttl=86400
        )
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, value=f"{f_record.name}.{f_zone.name}.", zone=r_zone
        )
        r_zone = Zone.objects.get(pk=r_record.zone.pk)

        self.assertEqual(r_zone.soa_serial, 1)
