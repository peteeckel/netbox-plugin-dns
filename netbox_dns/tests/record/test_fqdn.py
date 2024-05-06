from django.test import TestCase

from netbox_dns.models import NameServer, Zone, Record, RecordTypeChoices


class RecordFQDNTestSet(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.record_data = {"type": RecordTypeChoices.AAAA, "value": "fe80:dead:beef::"}

        cls.zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="zone2.example.com", **zone_data),
        )
        for zone in cls.zones:
            zone.save()

    def test_fqdn(self):
        records = (
            Record(name="name1", zone=self.zones[0], **self.record_data),
            Record(name="@", zone=self.zones[0], **self.record_data),
            Record(
                name="name3.zone1.example.com.", zone=self.zones[0], **self.record_data
            ),
            Record(name="name4.sub1", zone=self.zones[0], **self.record_data),
        )
        for record in records:
            record.save()

        self.assertEqual(records[0].fqdn, "name1.zone1.example.com.")
        self.assertEqual(records[1].fqdn, "zone1.example.com.")
        self.assertEqual(records[2].fqdn, "name3.zone1.example.com.")
        self.assertEqual(records[3].fqdn, "name4.sub1.zone1.example.com.")

    def test_fqdn_modify_record_name(self):
        record = Record.objects.create(
            name="name1", zone=self.zones[0], **self.record_data
        )

        self.assertEqual(record.fqdn, "name1.zone1.example.com.")

        record.name = "name2"
        record.save()

        self.assertEqual(record.fqdn, "name2.zone1.example.com.")

    def test_fqdn_modify_zone_name(self):
        zone = self.zones[0]

        record = Record.objects.create(name="name1", zone=zone, **self.record_data)

        self.assertEqual(record.fqdn, "name1.zone1.example.com.")

        zone.name = "zone3.example.com"
        zone.save()
        record.refresh_from_db()

        self.assertEqual(record.fqdn, "name1.zone3.example.com.")

    def test_fqdn_modify_record_zone(self):
        zone1 = self.zones[0]
        zone2 = self.zones[1]

        record = Record.objects.create(name="name1", zone=zone1, **self.record_data)

        self.assertEqual(record.fqdn, "name1.zone1.example.com.")

        record.zone = zone2
        record.save()

        self.assertEqual(record.fqdn, "name1.zone2.example.com.")
