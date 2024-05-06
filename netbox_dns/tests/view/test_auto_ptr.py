import ipaddress

from django.test import TestCase


from netbox_dns.models import View, Zone, NameServer, Record, RecordTypeChoices


def reverse_name(address, reverse_zone):
    reverse_pointer = ipaddress.ip_address(address).reverse_pointer
    zone_name = f"{reverse_zone.name}."

    if reverse_pointer.endswith(reverse_zone.name):
        return reverse_pointer[: -len(zone_name)]

    return f"{reverse_pointer}."


class ViewAutoPTRTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.views = [
            View(name="view1"),
            View(name="view2"),
        ]
        View.objects.bulk_create(cls.views)

        cls.zones = [
            Zone(
                name="zone1.example.com",
                **zone_data,
            ),
            Zone(
                name="zone1.example.com",
                **zone_data,
                view=cls.views[0],
            ),
            Zone(
                name="zone1.example.com",
                **zone_data,
                view=cls.views[1],
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **zone_data,
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **zone_data,
                view=cls.views[0],
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **zone_data,
                view=cls.views[1],
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **zone_data,
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **zone_data,
                view=cls.views[0],
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **zone_data,
                view=cls.views[1],
            ),
        ]
        for zone in cls.zones:
            zone.save()

    def test_create_ipv4_ptr_same_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )
        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_create_ipv4_ptr_missing_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_create_ipv4_ptr_added_view(self):
        f_zone = self.zones[0]
        r_zone = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_create_ipv4_ptr_different_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[5]

        name = "test1"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_remove_ipv4_ptr_same_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        f_record.delete()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_remove_ipv4_ptr_missing_view(self):
        f_zone1 = self.zones[0]
        f_zone2 = self.zones[1]
        r_zone2 = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_remove_ipv4_ptr_different_view(self):
        f_zone1 = self.zones[1]
        f_zone2 = self.zones[2]
        r_zone2 = self.zones[5]

        name = "test1"
        address = "10.0.1.42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_remove_ipv4_ptr_added_view(self):
        f_zone1 = self.zones[1]
        f_zone2 = self.zones[0]
        r_zone2 = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_create_multiple_ipv4_with_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[4]

        names = ["test1", "test2", "test3", "test4"]
        address = "10.0.1.42"

        for name in names:
            Record.objects.create(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.A,
                value=address,
            )

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR,
            zone=r_zone,
            name=reverse_name(address, r_zone),
        )
        for r_record in r_records:
            self.assertTrue(
                r_record.value in [f"{name}.{f_zone.name}." for name in names]
            )

    def test_create_duplicate_ipv4_with_view_disable_ptr_1(self):
        f_zone = self.zones[1]
        r_zone = self.zones[4]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.A,
            value=address,
            disable_ptr=True,
        )

        Record.objects.create(
            zone=f_zone,
            name=name2,
            type=RecordTypeChoices.A,
            value=address,
        )

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_create_duplicate_ipv4_with_view_disable_ptr_2(self):
        f_zone = self.zones[1]
        r_zone = self.zones[4]

        name1 = "test1"
        name2 = "test2"
        address = "10.0.1.42"

        Record.objects.create(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.A,
            value=address,
        )

        Record.objects.create(
            zone=f_zone,
            name=name2,
            type=RecordTypeChoices.A,
            value=address,
            disable_ptr=True,
        )

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name1}.{f_zone.name}.")

    def test_create_ipv6_ptr_same_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )
        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_create_ipv6_ptr_missing_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_create_ipv6_ptr_added_view(self):
        f_zone = self.zones[0]
        r_zone = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_create_ipv6_ptr_different_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[8]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_remove_ipv6_ptr_same_view(self):
        f_zone = self.zones[1]
        r_zone = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record.objects.create(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        f_record.delete()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_remove_ipv6_ptr_missing_view(self):
        f_zone1 = self.zones[0]
        f_zone2 = self.zones[1]
        r_zone2 = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_remove_ipv6_ptr_added_view(self):
        f_zone1 = self.zones[1]
        f_zone2 = self.zones[0]
        r_zone2 = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_remove_ipv6_ptr_different_view(self):
        f_zone1 = self.zones[1]
        f_zone2 = self.zones[2]
        r_zone2 = self.zones[8]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record1 = Record.objects.create(
            zone=f_zone1,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        Record.objects.create(
            zone=f_zone2,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        f_record1.delete()

        r_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR,
            zone=r_zone2,
            name=reverse_name(address, r_zone2),
        )

        self.assertEqual(r_record2.value, f"{name}.{f_zone2.name}.")

    def test_create_multiple_ipv6(self):
        f_zone = self.zones[1]
        r_zone = self.zones[7]

        names = ["test1", "test2", "test3", "test4"]
        address = "fe80:dead:beef:1::42"

        for name in names:
            Record.objects.create(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.AAAA,
                value=address,
            )

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR,
            zone=r_zone,
            name=reverse_name(address, r_zone),
        )
        for r_record in r_records:
            self.assertTrue(
                r_record.value in [f"{name}.{f_zone.name}." for name in names]
            )

    def test_create_duplicate_ipv6_with_view_disable_ptr_1(self):
        f_zone = self.zones[1]
        r_zone = self.zones[7]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
            disable_ptr=True,
        )

        Record.objects.create(
            zone=f_zone,
            name=name2,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name2}.{f_zone.name}.")

    def test_create_duplicate_ipv6_with_view_disable_ptr_2(self):
        f_zone = self.zones[1]
        r_zone = self.zones[7]

        name1 = "test1"
        name2 = "test2"
        address = "fe80:dead:beef:1::42"

        Record.objects.create(
            zone=f_zone,
            name=name1,
            type=RecordTypeChoices.AAAA,
            value=address,
        )

        Record.objects.create(
            zone=f_zone,
            name=name2,
            type=RecordTypeChoices.AAAA,
            value=address,
            disable_ptr=True,
        )

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name1}.{f_zone.name}.")
