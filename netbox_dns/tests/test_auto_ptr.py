import re
import ipaddress

from django.test import TestCase
from django.db.utils import IntegrityError

from netbox_dns.models import NameServer, Zone, Record


def reverse_name(address, reverse_zone):
    reverse_pointer = ipaddress.ip_address(address).reverse_pointer
    zone_name = f'{reverse_zone.name.rstrip(".")}.'

    if reverse_pointer.endswith(reverse_zone.name):
        return reverse_pointer[: -len(zone_name)]
    else:
        return f"{reverse_pointer}."


class AutoPTRTest(TestCase):

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
            Zone(name="2.0.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(name="1.1.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(name="0.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(name="2.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
            Zone(
                name="2.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
            Zone(
                name="1.1.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
            Zone(
                name="0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
            Zone(
                name="2.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
            ),
        ]
        Zone.objects.bulk_create(cls.zones)

    def test_create_ipv4_ptr(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()
        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_remove_ipv4_ptr(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        f_record.delete()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
            )

    def test_create_duplicate_ipv4(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        f_record1 = Record(
            zone=f_zone, name=name1, type=Record.A, value=address, **self.record_data
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone, name=name2, type=Record.A, value=address, **self.record_data
        )
        self.assertRaises(IntegrityError, f_record2.save)

    def test_create_duplicate_ipv4_disable_ptr_1(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=Record.A,
            value=address,
            disable_ptr=True,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone, name=name2, type=Record.A, value=address, **self.record_data
        )
        f_record2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_create_duplicate_ipv4_disable_ptr_2(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        f_record1 = Record(
            zone=f_zone, name=name1, type=Record.A, value=address, **self.record_data
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name2,
            type=Record.A,
            value=address,
            disable_ptr=True,
            **self.record_data,
        )
        f_record2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name1}.{f_zone.name}.")

    def test_change_name_ipv4(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name1, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        f_record.name = name2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_change_address_within_zone_ipv4(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name = "test1"
        address1 = "10.0.1.23"
        address2 = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address2, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_change_address_outside_zone_ipv4_old_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name = "test1"
        address1 = "10.0.1.23"
        address2 = "10.0.2.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=Record.PTR, zone=r_zone, name=reverse_name(address1, r_zone)
            )

    def test_change_address_outside_zone_ipv4_new_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        name = "test1"
        address1 = "10.0.1.23"
        address2 = "10.0.2.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address2, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_change_address_outside_zone_ipv4_no_zone(self):
        f_zone = self.zones[0]

        name = "test1"
        address1 = "10.0.1.23"
        address2 = "10.3.1.23"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(type=Record.PTR, value=f"{name}.{f_zone.name}.")

    def test_change_ttl_ipv4(self):
        f_zone = self.zones[0]
        r_zone = self.zones[1]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        f_record.ttl = 98765
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.ttl, 98765)

    def test_ipv4_delete_ptr_zone_with_parent(self):
        f_zone = self.zones[0]

        r_zone1 = self.zones[1]
        r_zone2 = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        r_zone1.delete()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone2, name=reverse_name(address, r_zone2)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_create_ptr_zone_with_parent(self):
        f_zone = self.zones[0]

        r_zone1 = self.zones[5]

        name = "test1"
        address = "10.2.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        r_zone2 = Zone(
            name="1.2.10.in-addr.arpa", **self.zone_data, soa_mname=self.nameserver
        )
        r_zone2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone2, name=reverse_name(address, r_zone2)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_create_ptr_zone_without_parent(self):
        f_zone = self.zones[0]

        name = "test1"
        address = "10.3.1.42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.A, value=address, **self.record_data
        )
        f_record.save()

        r_zone = Zone(
            name="1.3.10.in-addr.arpa", **self.zone_data, soa_mname=self.nameserver
        )
        r_zone.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_create_ipv6_ptr(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()
        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_remove_ipv6_ptr(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        f_record.delete()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
            )

    def test_create_duplicate_ipv6(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone, name=name1, type=Record.AAAA, value=address, **self.record_data
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone, name=name2, type=Record.AAAA, value=address, **self.record_data
        )
        self.assertRaises(IntegrityError, f_record2.save)

    def test_create_duplicate_ipv6_disable_ptr_1(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone,
            name=name1,
            type=Record.AAAA,
            value=address,
            disable_ptr=True,
            **self.record_data,
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone, name=name2, type=Record.AAAA, value=address, **self.record_data
        )
        f_record2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_create_duplicate_ipv6_disable_ptr_2(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record(
            zone=f_zone, name=name1, type=Record.AAAA, value=address, **self.record_data
        )
        f_record1.save()

        f_record2 = Record(
            zone=f_zone,
            name=name2,
            type=Record.AAAA,
            value=address,
            disable_ptr=True,
            **self.record_data,
        )
        f_record2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name1}.{f_zone.name}.")

    def test_change_name_ipv6(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name1, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        f_record.name = name2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_change_address_within_zone_ipv6(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name = "test1"
        address1 = "fe80:dead:beef:1::23"
        address2 = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address2, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_change_address_outside_zone_ipv6_old_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name = "test1"
        address1 = "fe80:dead:beef:1::23"
        address2 = "fe80:dead:beef:2::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=Record.PTR, zone=r_zone, name=reverse_name(address1, r_zone)
            )

    def test_change_address_outside_zone_ipv6_new_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[7]

        name = "test1"
        address1 = "fe80:dead:beef:1::23"
        address2 = "fe80:dead:beef:2::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address2, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_change_address_outside_zone_ipv6_no_zone(self):
        f_zone = self.zones[0]

        name = "test1"
        address1 = "fe80:dead:beef:1::23"
        address2 = "fe80:dead:beef:31::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address1, **self.record_data
        )
        f_record.save()

        f_record.value = address2
        f_record.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(type=Record.PTR, value=f"{name}.{f_zone.name}.")

    def test_change_ttl_ipv6(self):
        f_zone = self.zones[0]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        f_record.ttl = 98765
        f_record.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.ttl, 98765)

    def test_ipv6_delete_ptr_zone_with_parent(self):
        f_zone = self.zones[0]

        r_zone1 = self.zones[6]
        r_zone2 = self.zones[9]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        r_zone1.delete()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone2, name=reverse_name(address, r_zone2)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_create_ptr_zone_with_parent(self):
        f_zone = self.zones[0]

        r_zone1 = self.zones[10]

        name = "test1"
        address = "fe80:dead:beef:21::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        r_zone2 = Zone(
            name="1.2.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
            **self.zone_data,
            soa_mname=self.nameserver,
        )
        r_zone2.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone2, name=reverse_name(address, r_zone2)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_create_ptr_zone_without_parent(self):
        f_zone = self.zones[0]

        name = "test1"
        address = "fe80:dead:beef:31::42"

        f_record = Record(
            zone=f_zone, name=name, type=Record.AAAA, value=address, **self.record_data
        )
        f_record.save()

        r_zone = Zone(
            name="1.3.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
            **self.zone_data,
            soa_mname=self.nameserver,
        )
        r_zone.save()

        r_record = Record.objects.get(
            type=Record.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")
