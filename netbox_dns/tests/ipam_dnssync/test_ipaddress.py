from copy import deepcopy

from netaddr import IPNetwork

from django.test import TestCase, override_settings
from django.core import management
from django.core.exceptions import ValidationError
from django.conf import settings

from ipam.models import IPAddress, Prefix
from ipam.choices import IPAddressStatusChoices

from netbox_dns.models import View, Zone, NameServer, Record
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


zone_defaults = settings.PLUGINS_CONFIG.get("netbox_dns")


class DNSsyncIPAddressTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        view = View.get_default_view()
        cls.zone = Zone.objects.create(name="zone1.example.com", **cls.zone_data)

        prefixes = (
            Prefix(prefix="10.0.0.0/24"),
            Prefix(prefix="fe80:dead:beef:0::/64"),
        )
        Prefix.objects.bulk_create(prefixes)

        view.prefixes.add(prefixes[0])
        view.prefixes.add(prefixes[1])

        management.call_command("setup_dnssync", verbosity=0)

    def test_create_ip_address(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.zone, self.zone)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))
        self.assertEqual(record4.type, RecordTypeChoices.A)
        self.assertEqual(record4.managed, True)
        self.assertEqual(record4.disable_ptr, False)
        self.assertEqual(record4.ttl, None)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.zone, self.zone)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))
        self.assertEqual(record6.type, RecordTypeChoices.AAAA)
        self.assertEqual(record6.managed, True)
        self.assertEqual(record6.disable_ptr, False)
        self.assertEqual(record6.ttl, None)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

    def test_create_ip_address_short_zone(self):
        Zone.objects.create(name="short", **self.zone_data)
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.short"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.short",
        )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())

    @override_settings(
        PLUGINS_CONFIG={
            "netbox_dns": {**zone_defaults, "dnssync_minimum_zone_labels": 1}
        }
    )
    def test_create_ip_address_short_zone_allow(self):
        Zone.objects.create(name="short", **self.zone_data)
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.short"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.short",
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)
        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)

    def test_create_ip_address_duplicate_record(self):
        records = (
            Record(
                name="name1", zone=self.zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ),
            Record(
                name="name2",
                zone=self.zone,
                type=RecordTypeChoices.AAAA,
                value="fe80:dead:beef::1",
            ),
        )
        for record in records:
            record.save()

        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
            )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A, managed=True))
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True)
        )

    def test_create_ip_address_duplicate_record_deactivate(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        test_settings["dnssync_conflict_deactivate"] = True

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            records = (
                Record(
                    name="name1",
                    zone=self.zone,
                    type=RecordTypeChoices.A,
                    value="10.0.0.1",
                ),
                Record(
                    name="name2",
                    zone=self.zone,
                    type=RecordTypeChoices.AAAA,
                    value="fe80:dead:beef::1",
                ),
            )
            for record in records:
                record.save()

            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
            )

            for record in records:
                record.refresh_from_db()
                self.assertTrue(record.status, RecordStatusChoices.STATUS_INACTIVE)
            self.assertTrue(
                Record.objects.filter(ipam_ip_address=ipv4_address).exists()
            )
            self.assertTrue(
                Record.objects.filter(ipam_ip_address=ipv6_address).exists()
            )

    def test_create_ip_address_duplicate_dnssync_record(self):
        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertEqual(
            IPAddress.objects.filter(address=IPNetwork("10.0.0.1/24")).count(), 2
        )
        self.assertEqual(
            IPAddress.objects.filter(address=IPNetwork("fe80:dead:beef::1/64")).count(),
            2,
        )
        self.assertEqual(
            Record.objects.filter(type=RecordTypeChoices.A, value="10.0.0.1").count(),
            2,
        )
        self.assertEqual(
            Record.objects.filter(
                type=RecordTypeChoices.AAAA, value="fe80:dead:beef::1"
            ).count(),
            2,
        )

    def test_create_ip_address_dnssync_record_rrset_ttl_conflict(self):
        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 42},
        )
        IPAddress.objects.create(
            address=IPNetwork("10.0.0.2/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 23},
        )
        IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 42},
        )
        IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::2/64"),
            dns_name="name2.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 23},
        )

        self.assertEqual(
            IPAddress.objects.filter(dns_name="name1.zone1.example.com").count(), 2
        )
        self.assertEqual(
            IPAddress.objects.filter(dns_name="name2.zone1.example.com").count(),
            2,
        )
        self.assertEqual(
            Record.objects.filter(
                type=RecordTypeChoices.A, fqdn="name1.zone1.example.com."
            ).count(),
            2,
        )
        self.assertEqual(
            Record.objects.filter(
                type=RecordTypeChoices.AAAA, fqdn="name2.zone1.example.com."
            ).count(),
            2,
        )

    def test_create_ip_address_ttl_rrset_conflict(self):
        records = (
            Record(
                name="name1",
                zone=self.zone,
                type=RecordTypeChoices.A,
                value="10.0.1.1",
                ttl=43200,
            ),
            Record(
                name="name2",
                zone=self.zone,
                type=RecordTypeChoices.AAAA,
                value="fe80:dead:beef:1::1",
                ttl=43200,
            ),
        )
        for record in records:
            record.save()

        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
            )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A, managed=True))
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True)
        )

    def test_create_ip_address_invalid_record(self):
        records = (
            Record(
                name="name1", zone=self.zone, type=RecordTypeChoices.CNAME, value="@"
            ),
            Record(
                name="name2", zone=self.zone, type=RecordTypeChoices.CNAME, value="@"
            ),
        )
        for record in records:
            record.save()

        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
            )

        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.A, managed=True).exists()
        )
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True).exists()
        )

    def test_create_ip_address_disable_ptr(self):
        Zone.objects.create(name="0.0.10.in-addr.arpa", **self.zone_data)
        Zone.objects.create(name="f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa", **self.zone_data)

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_disable_ptr": True},
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_disable_ptr": True},
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.zone, self.zone)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))
        self.assertEqual(record4.type, RecordTypeChoices.A)
        self.assertEqual(record4.managed, True)
        self.assertEqual(record4.disable_ptr, True)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.zone, self.zone)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))
        self.assertEqual(record6.type, RecordTypeChoices.AAAA)
        self.assertEqual(record6.managed, True)
        self.assertEqual(record6.disable_ptr, True)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.PTR).exists())

    def test_create_ip_address_ttl(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 86400},
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            custom_field_data={"ipaddress_dns_record_ttl": 86400},
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.zone, self.zone)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))
        self.assertEqual(record4.type, RecordTypeChoices.A)
        self.assertEqual(record4.managed, True)
        self.assertEqual(record4.ttl, 86400)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.zone, self.zone)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))
        self.assertEqual(record6.type, RecordTypeChoices.AAAA)
        self.assertEqual(record6.managed, True)
        self.assertEqual(record6.ttl, 86400)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

    def test_create_ip_address_dns_disabled(self):
        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_disabled": True},
        )
        IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            custom_field_data={"ipaddress_dns_disabled": True},
        )

        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.A, managed=True).exists()
        )
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True).exists()
        )

    def test_create_ip_address_status_inactive(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            status=IPAddressStatusChoices.STATUS_RESERVED,
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            status=IPAddressStatusChoices.STATUS_RESERVED,
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

    def test_create_ip_address_status_custom_active(self):
        test_settings = deepcopy(settings.PLUGINS_CONFIG["netbox_dns"])
        test_settings["dnssync_ipaddress_active_status"].append(
            IPAddressStatusChoices.STATUS_RESERVED
        )

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"),
                dns_name="name1.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_RESERVED,
            )
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_RESERVED,
            )

            record4 = Record.objects.get(ipam_ip_address=ipv4_address)
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

            record6 = Record.objects.get(ipam_ip_address=ipv6_address)
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

    def test_create_ip_address_status_custom_inactive(self):
        test_settings = deepcopy(settings.PLUGINS_CONFIG["netbox_dns"])
        test_settings["dnssync_ipaddress_active_status"].remove(
            IPAddressStatusChoices.STATUS_DHCP
        )

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"),
                dns_name="name1.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_DHCP,
            )
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_DHCP,
            )

            record4 = Record.objects.get(ipam_ip_address=ipv4_address)
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

            record6 = Record.objects.get(ipam_ip_address=ipv6_address)
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

    def test_update_ip_address_name(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.dns_name = "name3.zone1.example.com"
        ipv4_address.save()

        ipv6_address.dns_name = "name4.zone1.example.com"
        ipv6_address.save()

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)

    def test_update_ip_address_address(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.address = IPNetwork("10.0.0.2/24")
        ipv4_address.save()

        ipv6_address.address = IPNetwork("fe80:dead:beef::2/64")
        ipv6_address.save()

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))

    def test_update_ip_address_zone(self):
        Zone.objects.create(name="zone2.example.com", **self.zone_data)

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.dns_name = "name1.zone2.example.com"
        ipv4_address.save()

        ipv6_address.dns_name = "name2.zone2.example.com"
        ipv6_address.save()

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)
        self.assertFalse(
            Record.objects.filter(
                fqdn__startswith="name1.zone1.example.com", type=RecordTypeChoices.A
            ).exists()
        )

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)
        self.assertFalse(
            Record.objects.filter(
                fqdn__startswith="name2.zone1.example.com", type=RecordTypeChoices.AAAA
            ).exists()
        )

    def test_update_ip_address_name_missing_zone(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.dns_name = "name1.zone2.example.com"
        ipv4_address.save()

        ipv6_address.dns_name = "name2.zone2.example.com"
        ipv6_address.save()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())

    def test_update_ip_address_name_duplicate_record(self):
        records = (
            Record(
                name="name3", zone=self.zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ),
            Record(
                name="name4",
                zone=self.zone,
                type=RecordTypeChoices.AAAA,
                value="fe80:dead:beef::1",
            ),
        )
        for record in records:
            record.save()

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.dns_name = "name3.zone1.example.com"
        with self.assertRaises(ValidationError):
            ipv4_address.save()

        ipv6_address.dns_name = "name4.zone1.example.com"
        with self.assertRaises(ValidationError):
            ipv6_address.save()

        ipv4_address.refresh_from_db()
        self.assertEqual(ipv4_address.dns_name, "name1.zone1.example.com")
        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)

        ipv6_address.refresh_from_db()
        self.assertEqual(ipv6_address.dns_name, "name2.zone1.example.com")
        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)

    def test_update_ip_address_address_duplicate_record(self):
        records = (
            Record(
                name="name1", zone=self.zone, type=RecordTypeChoices.A, value="10.0.0.2"
            ),
            Record(
                name="name2",
                zone=self.zone,
                type=RecordTypeChoices.AAAA,
                value="fe80:dead:beef::2",
            ),
        )
        for record in records:
            record.save()

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.address = IPNetwork("10.0.0.2/24")
        with self.assertRaises(ValidationError):
            ipv4_address.save()

        ipv6_address.address = IPNetwork("fe80:dead:beef::2/64")
        with self.assertRaises(ValidationError):
            ipv6_address.save()

        ipv4_address.refresh_from_db()
        self.assertEqual(ipv4_address.address, IPNetwork("10.0.0.1/24"))
        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))

        ipv6_address.refresh_from_db()
        self.assertEqual(ipv6_address.address, IPNetwork("fe80:dead:beef::1/64"))
        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))

    def test_update_ip_address_invalid_record(self):
        records = (
            Record(
                name="name3",
                zone=self.zone,
                type=RecordTypeChoices.CNAME,
                value="invalid",
            ),
            Record(
                name="name4",
                zone=self.zone,
                type=RecordTypeChoices.CNAME,
                value="invalid",
            ),
        )
        for record in records:
            record.save()

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.dns_name = "name3.zone1.example.com"
        with self.assertRaises(ValidationError):
            ipv4_address.save()

        ipv6_address.dns_name = "name4.zone1.example.com"
        with self.assertRaises(ValidationError):
            ipv6_address.save()

        ipv4_address.refresh_from_db()
        self.assertEqual(ipv4_address.dns_name, "name1.zone1.example.com")
        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.fqdn.rstrip("."), ipv4_address.dns_name)

        ipv6_address.refresh_from_db()
        self.assertEqual(ipv6_address.dns_name, "name2.zone1.example.com")
        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.fqdn.rstrip("."), ipv6_address.dns_name)

    def test_update_ip_address_disable_ptr(self):
        reverse4_zone = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data
        )
        reverse6_zone = Zone.objects.create(
            name="f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa", **self.zone_data
        )

        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertTrue(
            Record.objects.filter(
                zone=reverse4_zone, type=RecordTypeChoices.PTR
            ).first(),
            record4.ptr_record,
        )

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertTrue(
            Record.objects.filter(
                zone=reverse6_zone, type=RecordTypeChoices.PTR
            ).first(),
            record6.ptr_record,
        )

        ipv4_address.custom_field_data = {"ipaddress_dns_record_disable_ptr": True}
        ipv4_address.save()
        ipv6_address.custom_field_data = {"ipaddress_dns_record_disable_ptr": True}
        ipv6_address.save()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.PTR).exists())

    def test_update_ip_address_ttl(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.custom_field_data = {"ipaddress_dns_record_ttl": 86400}
        ipv4_address.save()
        ipv6_address.custom_field_data = {"ipaddress_dns_record_ttl": 86400}
        ipv6_address.save()

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.ttl, 86400)
        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.ttl, 86400)

    def test_update_ip_address_ttl_rrset_conflict(self):
        pass

    def test_update_ip_address_status_inactive(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

        ipv4_address.status = IPAddressStatusChoices.STATUS_RESERVED
        ipv4_address.save()

        ipv6_address.status = IPAddressStatusChoices.STATUS_RESERVED
        ipv6_address.save()

        record4.refresh_from_db()
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

        record6.refresh_from_db()
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

    def test_update_ip_address_status_active(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            status=IPAddressStatusChoices.STATUS_RESERVED,
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
            status=IPAddressStatusChoices.STATUS_RESERVED,
        )

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

        ipv4_address.status = IPAddressStatusChoices.STATUS_ACTIVE
        ipv4_address.save()

        ipv6_address.status = IPAddressStatusChoices.STATUS_ACTIVE
        ipv6_address.save()

        record4.refresh_from_db()
        self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

        record6.refresh_from_db()
        self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

    def test_update_ip_address_status_custom_active(self):
        test_settings = deepcopy(settings.PLUGINS_CONFIG["netbox_dns"])
        test_settings["dnssync_ipaddress_active_status"].append(
            IPAddressStatusChoices.STATUS_RESERVED
        )

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"),
                dns_name="name1.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_DEPRECATED,
            )
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_DEPRECATED,
            )

            record4 = Record.objects.get(ipam_ip_address=ipv4_address)
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

            record6 = Record.objects.get(ipam_ip_address=ipv6_address)
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

            ipv4_address.status = IPAddressStatusChoices.STATUS_RESERVED
            ipv4_address.save()

            ipv6_address.status = IPAddressStatusChoices.STATUS_RESERVED
            ipv6_address.save()

            record4.refresh_from_db()
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

            record6.refresh_from_db()
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

    def test_update_ip_address_status_custom_inactive(self):
        test_settings = deepcopy(settings.PLUGINS_CONFIG["netbox_dns"])
        test_settings["dnssync_ipaddress_active_status"].remove(
            IPAddressStatusChoices.STATUS_DHCP
        )

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"),
                dns_name="name1.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_ACTIVE,
            )
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
                status=IPAddressStatusChoices.STATUS_ACTIVE,
            )

            record4 = Record.objects.get(ipam_ip_address=ipv4_address)
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_ACTIVE)

            record6 = Record.objects.get(ipam_ip_address=ipv6_address)
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_ACTIVE)

            ipv4_address.status = IPAddressStatusChoices.STATUS_DHCP
            ipv4_address.save()

            ipv6_address.status = IPAddressStatusChoices.STATUS_DHCP
            ipv6_address.save()

            record4.refresh_from_db()
            self.assertEqual(record4.status, RecordStatusChoices.STATUS_INACTIVE)

            record6.refresh_from_db()
            self.assertEqual(record6.status, RecordStatusChoices.STATUS_INACTIVE)

    def test_delete_ip_address(self):
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        ipv6_address = IPAddress.objects.create(
            address=IPNetwork("fe80:dead:beef::1/64"),
            dns_name="name2.zone1.example.com",
        )

        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv4_address).exists())
        self.assertTrue(Record.objects.filter(ipam_ip_address=ipv6_address).exists())

        ipv4_address.delete()
        ipv6_address.delete()

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A).exists())
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())
