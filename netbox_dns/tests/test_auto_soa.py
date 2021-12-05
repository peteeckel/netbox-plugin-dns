import re

from django.test import TestCase

from netbox_dns.models import NameServer, Zone, Record


def parse_soa_value(soa):
    soa_match = re.match(
        r"^\((\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\)", soa
    )
    return {
        "soa_mname": soa_match.group(1),
        "soa_rname": soa_match.group(2),
        "soa_serial": int(soa_match.group(3)),
        "soa_refresh": int(soa_match.group(4)),
        "soa_retry": int(soa_match.group(5)),
        "soa_expire": int(soa_match.group(6)),
        "soa_minimum": int(soa_match.group(7)),
    }


class AutoSOATest(TestCase):

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
        cls.nameservers = [
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
        ]
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zone = Zone.objects.create(
            name="zone1.example.com", **cls.zone_data, soa_mname=cls.nameservers[0]
        )

    def test_zone_soa(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        soa_records = Record.objects.filter(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_records[0].value)

        self.assertTrue(
            all(
                (
                    zone.soa_mname.name == soa.get("soa_mname"),
                    zone.soa_rname == soa.get("soa_rname"),
                    zone.soa_serial == soa.get("soa_serial"),
                    zone.soa_refresh == soa.get("soa_refresh"),
                    zone.soa_retry == soa.get("soa_retry"),
                    zone.soa_expire == soa.get("soa_expire"),
                    zone.soa_minimum == soa.get("soa_minimum"),
                    zone.soa_ttl == soa_records[0].ttl,
                    len(soa_records) == 1,
                )
            )
        )

    def test_zone_soa_change_mname(self):
        zone = self.zone
        nameserver2 = self.nameservers[1]

        zone.soa_mname = nameserver2
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(nameserver2.name, soa.get("soa_mname"))

    def test_zone_soa_change_rname(self):
        zone = self.zone
        rname = "new-hostmaster.example.com"

        zone.soa_rname = rname
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(rname, soa.get("soa_rname"))

    def test_zone_soa_change_serial(self):
        zone = self.zone
        serial = 42

        zone.soa_serial = serial
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(serial, soa.get("soa_serial"))

    def test_zone_soa_change_refresh(self):
        zone = self.zone
        refresh = 23

        zone.soa_refresh = refresh
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(refresh, soa.get("soa_refresh"))

    def test_zone_soa_change_retry(self):
        zone = self.zone
        retry = 2342

        zone.soa_retry = retry
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(retry, soa.get("soa_retry"))

    def test_zone_soa_change_expire(self):
        zone = self.zone
        expire = 4223

        zone.soa_expire = expire
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(expire, soa.get("soa_expire"))

    def test_zone_soa_change_minimum(self):
        zone = self.zone
        minimum = 4223

        zone.soa_minimum = minimum
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)
        soa = parse_soa_value(soa_record.value)

        self.assertEqual(minimum, soa.get("soa_minimum"))

    def test_zone_soa_change_ttl(self):
        zone = self.zone
        ttl = 422342

        zone.soa_ttl = ttl
        zone.save()

        soa_record = Record.objects.get(type=Record.SOA, zone=zone)

        self.assertEqual(ttl, soa_record.ttl)
