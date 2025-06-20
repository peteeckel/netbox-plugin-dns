from dns import rdata

from django.test import TestCase
from django.db.models import ProtectedError

from netbox_dns.models import NameServer, Record, Zone
from netbox_dns.choices import RecordTypeChoices, ZoneStatusChoices, RecordStatusChoices


class ZoneAutoNSTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zone_data = {
            "soa_mname": cls.nameservers[0],
            "soa_rname": "hostmaster.example.com",
        }

        cls.zone = Zone.objects.create(name="zone1.example.com", **cls.zone_data)

    def test_zone_without_ns(self):
        zone = self.zone

        ns_records = Record.objects.filter(
            zone=zone, type=RecordTypeChoices.NS, managed=True
        )
        self.assertEqual(0, len(ns_records))

    def test_zone_without_ns_error(self):
        zone = self.zone

        ns_errors = zone.check_nameservers()[1]
        self.assertIn(f"No nameservers are configured for zone {zone.name}", ns_errors)

    def test_zone_with_ns(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)

        ns_records = Record.objects.filter(
            zone=zone, type=RecordTypeChoices.NS, managed=True, name="@"
        )
        ns_values = [ns.value for ns in ns_records]
        self.assertEqual([f"{nameserver.name}."], ns_values)

    def test_zone_with_ns_no_warning(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)
        ns_warnings = zone.check_nameservers()[0]
        self.assertEqual([], ns_warnings)

    def test_zone_with_ns_warning(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        ns_zone = Zone.objects.create(name="example.com", **self.zone_data)

        zone.nameservers.add(nameserver)
        ns_warnings = zone.check_nameservers()[0]
        self.assertIn(
            f"Nameserver {nameserver.name} does not have an active address record in zone {ns_zone.name}",
            ns_warnings,
        )

    def test_inactive_zone_with_ns_warning(self):
        nameserver = self.nameservers[0]
        ns_zone = Zone.objects.create(
            name="example.com",
            **self.zone_data,
            status=ZoneStatusChoices.STATUS_RESERVED,
        )
        ns_zone.nameservers.add(nameserver)

        ns_warnings = ns_zone.check_nameservers()[0]
        self.assertIn(
            f"Nameserver {nameserver.name} does not have an active address record in zone {ns_zone.name}",
            ns_warnings,
        )

    def test_inactive_zone_with_ns_and_address_no_warning(self):
        nameserver = self.nameservers[0]
        ns_zone = Zone.objects.create(
            name="example.com",
            **self.zone_data,
            status=ZoneStatusChoices.STATUS_RESERVED,
        )
        ns_zone.nameservers.add(nameserver)

        ns_record = Record.objects.create(
            zone=ns_zone,
            name="ns1",
            type=RecordTypeChoices.A,
            value="10.0.0.23",
            ttl=86400,
        )
        ns_record.save()

        ns_warnings = ns_zone.check_nameservers()[0]
        self.assertEqual([], ns_warnings)

    def test_inactive_zone_with_ns_and_inactive_address_warning(self):
        nameserver = self.nameservers[0]
        ns_zone = Zone.objects.create(
            name="example.com",
            **self.zone_data,
            status=ZoneStatusChoices.STATUS_RESERVED,
        )
        ns_zone.nameservers.add(nameserver)

        ns_record = Record.objects.create(
            zone=ns_zone,
            name="ns1",
            type=RecordTypeChoices.A,
            value="10.0.0.23",
            ttl=86400,
            status=RecordStatusChoices.STATUS_INACTIVE,
        )
        ns_record.save()

        ns_warnings = ns_zone.check_nameservers()[0]
        self.assertIn(
            f"Nameserver {nameserver.name} does not have an active address record in zone {ns_zone.name}",
            ns_warnings,
        )

    def test_zone_with_multiple_ns(self):
        zone = self.zone
        nameserver1 = self.nameservers[0]
        nameserver2 = self.nameservers[1]

        zone.nameservers.add(nameserver1)
        zone.nameservers.add(nameserver2)

        ns_records = Record.objects.filter(
            zone=zone, type=RecordTypeChoices.NS, managed=True, name="@"
        )
        ns_values = [ns.value for ns in ns_records]
        self.assertEqual(
            [f"{nameserver1.name}.", f"{nameserver2.name}."], sorted(ns_values)
        )

    def test_zone_with_multiple_ns_remove_ns(self):
        zone = self.zone
        nameserver1 = self.nameservers[0]
        nameserver2 = self.nameservers[1]

        zone.nameservers.add(nameserver1)
        zone.nameservers.add(nameserver2)

        zone.nameservers.remove(nameserver1)

        ns_records = Record.objects.filter(
            zone=zone, type=RecordTypeChoices.NS, managed=True, name="@"
        )
        ns_values = [ns.value for ns in ns_records]
        self.assertEqual([f"{nameserver2.name}."], ns_values)

    def test_zone_add_ns_ns_record_added(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)

        ns_record = Record.objects.get(
            name="@", zone=zone, type=RecordTypeChoices.NS, value=f"{nameserver.name}."
        )
        self.assertEqual(nameserver.name, ns_record.value.rstrip("."))

    def test_zone_remove_ns_ns_record_removed(self):
        zone = self.zone
        nameserver = self.nameservers[1]

        zone.nameservers.add(nameserver)

        ns_record = Record.objects.get(
            name="@", zone=zone, type=RecordTypeChoices.NS, value=f"{nameserver.name}."
        )
        self.assertEqual(nameserver.name, ns_record.value.rstrip("."))

        zone.nameservers.remove(nameserver)

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver.name}.",
            )

    def test_delete_ns_ns_record_removed(self):
        zone = self.zone
        nameserver = self.nameservers[1]

        zone.nameservers.add(nameserver)

        ns_record = Record.objects.get(
            name="@", zone=zone, type=RecordTypeChoices.NS, value=f"{nameserver.name}."
        )
        self.assertEqual(nameserver.name, ns_record.value.rstrip("."))

        nameserver.delete()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver.name}.",
            )

    def test_delete_soa_ns_exception(self):
        nameserver = self.nameservers[0]

        with self.assertRaisesRegex(
            ProtectedError, r"protected foreign keys: 'Zone\.soa_mname'."
        ):
            nameserver.delete()

    def test_delete_soa_ns_exception_ns_record_retained(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)

        with self.assertRaisesRegex(
            ProtectedError, r"protected foreign keys: 'Zone\.soa_mname'."
        ):
            nameserver.delete()

        ns_record = Record.objects.get(
            name="@", zone=zone, type=RecordTypeChoices.NS, value=f"{nameserver.name}."
        )
        self.assertEqual(nameserver.name, ns_record.value.rstrip("."))

    def test_rename_ns_ns_record_updated(self):
        zone = self.zone
        nameserver = self.nameservers[1]

        zone.nameservers.add(nameserver)

        nameserver.name = "test.example.org"
        nameserver.save()

        ns_record = Record.objects.get(
            name="@", zone=zone, type=RecordTypeChoices.NS, value=f"{nameserver.name}."
        )
        self.assertEqual(nameserver.name, ns_record.value.rstrip("."))

    def test_rename_ns_soa_record_updated(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        nameserver.name = "test.example.org"
        nameserver.save()

        soa_record = Record.objects.get(name="@", zone=zone, type=RecordTypeChoices.SOA)
        soa_rdata = rdata.from_text("IN", "SOA", soa_record.value)

        self.assertEqual(nameserver.name, soa_rdata.mname.to_text().rstrip("."))
