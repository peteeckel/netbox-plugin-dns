from netaddr import IPNetwork

from unittest import skip

from django.test import TestCase
from django.core import management
from django.core.exceptions import ValidationError

from ipam.models import IPAddress, Prefix

from netbox_dns.models import View, Zone, NameServer, Record
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


class AutoDNSIPAddressTestCase(TestCase):
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

        management.call_command("setup_autodns")

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
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            ipv6_address = IPAddress.objects.create(
                address=IPNetwork("fe80:dead:beef::1/64"),
                dns_name="name2.zone1.example.com",
            )

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.A, managed=True))
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True)
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
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            ipv6_address = IPAddress.objects.create(
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
            ipv4_address = IPAddress.objects.create(
                address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
            )
        with self.assertRaises(ValidationError):
            ipv6_address = IPAddress.objects.create(
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
        reverse4_zone = Zone.objects.create(
            name="0.0.10.in-addr.arpa", **self.zone_data
        )
        reverse6_zone = Zone.objects.create(
            name="f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa", **self.zone_data
        )

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
        ipv4_address = IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"),
            dns_name="name1.zone1.example.com",
            custom_field_data={"ipaddress_dns_disabled": True},
        )
        ipv6_address = IPAddress.objects.create(
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

    @skip("status dependent autodns not implemented yet")
    def test_create_ip_address_status_inactive(self):
        pass

    @skip("status dependent autodns not implemented yet")
    def test_create_ip_address_status_custom(self):
        pass

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

        ipv4_address.address = address = IPNetwork("10.0.0.2/24")
        ipv4_address.save()

        ipv6_address.address = address = IPNetwork("fe80:dead:beef::2/64")
        ipv6_address.save()

        record4 = Record.objects.get(ipam_ip_address=ipv4_address)
        self.assertEqual(record4.value, str(ipv4_address.address.ip))

        record6 = Record.objects.get(ipam_ip_address=ipv6_address)
        self.assertEqual(record6.value, str(ipv6_address.address.ip))

    def test_update_ip_address_zone(self):
        new_zone = Zone.objects.create(name="zone2.example.com", **self.zone_data)

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

    @skip("status dependent autodns not implemented yet")
    def test_update_ip_address_status_inactive(self):
        pass

    @skip("status dependent autodns not implemented yet")
    def test_update_ip_address_status_active(self):
        pass

    @skip("status dependent autodns not implemented yet")
    def test_update_ip_address_status_custom(self):
        pass

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