from django.test import TestCase

from netbox_dns.models import NameServer, Zone, Record


class AutoNSTest(TestCase):

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

        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zone = Zone.objects.create(
            name="zone1.example.com", **cls.zone_data, soa_mname=cls.nameservers[0]
        )

    def test_zone_without_ns(self):
        zone = self.zone

        ns_records = Record.objects.filter(zone=zone, type=Record.NS, managed=True)
        self.assertEqual(0, len(ns_records))

    def test_zone_without_ns_error(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        ns_warnings, ns_errors = zone.check_nameservers()
        self.assertIn(f"No nameservers are configured for zone {zone.name}", ns_errors)

    def test_zone_with_ns(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)

        ns_records = Record.objects.filter(
            zone=zone, type=Record.NS, managed=True, name="@"
        )
        ns_values = [ns.value for ns in ns_records]
        self.assertEqual([f"{nameserver.name}."], ns_values)

    def test_zone_with_ns_no_warning(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        zone.nameservers.add(nameserver)
        ns_warnings, ns_errors = zone.check_nameservers()
        self.assertEqual([], ns_warnings)

    def test_zone_with_ns_warning(self):
        zone = self.zone
        nameserver = self.nameservers[0]

        ns_zone = Zone.objects.create(
            name="example.com", **self.zone_data, soa_mname=nameserver
        )

        zone.nameservers.add(nameserver)
        ns_warnings, ns_errors = zone.check_nameservers()
        self.assertIn(
            f"Nameserver {nameserver.name} does not have an address record in zone {ns_zone.name}",
            ns_warnings,
        )

    def test_zone_with_multiple_ns(self):
        zone = self.zone
        nameserver1 = self.nameservers[0]
        nameserver2 = self.nameservers[1]

        zone.nameservers.add(nameserver1)
        zone.nameservers.add(nameserver2)

        ns_records = Record.objects.filter(
            zone=zone, type=Record.NS, managed=True, name="@"
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
            zone=zone, type=Record.NS, managed=True, name="@"
        )
        ns_values = [ns.value for ns in ns_records]
        self.assertEqual([f"{nameserver2.name}."], ns_values)
