import ipaddress

from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


from netbox_dns.models import View, Zone, NameServer, Record, RecordTypeChoices


def reverse_name(address, reverse_zone):
    reverse_pointer = ipaddress.ip_address(address).reverse_pointer
    zone_name = f"{reverse_zone.name}."

    if reverse_pointer.endswith(reverse_zone.name):
        return reverse_pointer[: -len(zone_name)]

    return f"{reverse_pointer}."


class ViewZoneTestCase(TestCase):
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

        cls.views = [
            View(name="view1"),
            View(name="view2"),
            View(name="view3"),
        ]
        View.objects.bulk_create(cls.views)

        cls.zones = [
            Zone(
                name="zone1.example.com",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=None,
            ),
            Zone(
                name="zone1.example.com",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=cls.views[0],
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=None,
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=cls.views[0],
            ),
            Zone(
                name="1.0.10.in-addr.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=cls.views[1],
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=None,
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=cls.views[0],
            ),
            Zone(
                name="1.0.0.0.f.e.e.b.d.a.e.d.0.8.e.f.ip6.arpa",
                **cls.zone_data,
                soa_mname=cls.nameserver,
                view=cls.views[1],
            ),
        ]
        for zone in cls.zones:
            zone.save()

    def test_ipv4_add_view_to_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        r_zone = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_add_view_to_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv4_remove_view_from_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = None
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_remove_view_from_zone_old_ptr_removed(self):
        self.zones[0].delete()

        f_zone = self.zones[1]
        r_zone = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = None
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv4_change_view_of_zone_new_ptr_added(self):
        f_zone = self.zones[1]
        self.zones[3].delete()
        r_zone = self.zones[4]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_change_view_of_zone_old_ptr_removed(self):
        f_zone = self.zones[1]
        r_zone = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv4_add_view_to_ptr_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = self.views[2]
        r_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_add_view_to_ptr_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = self.views[2]
        r_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv4_remove_view_from_ptr_zone_new_ptr_added(self):
        f_zone = self.zones[0]

        r_zone = self.zones[2]
        r_zone.view = self.views[2]
        r_zone.save()

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = None
        r_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv4_remove_view_from_ptr_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[2]
        r_zone.view = self.views[2]
        r_zone.save()

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = None
        r_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv4_add_view_to_zone_no_ptr_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.A,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[2]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR, name=reverse_name(address, r_zone)
            )

    def test_ipv4_add_view_multiple_ptr(self):
        f_zone1 = self.zones[1]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=None,
        )
        f_zone2.save()
        r_zone = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.A,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = self.views[0]
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_ipv4_remove_view_multiple_ptr(self):
        f_zone1 = self.zones[0]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=self.views[1],
        )
        f_zone2.save()
        r_zone = self.zones[2]

        name = "test1"
        address = "10.0.1.42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.A,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = None
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_ipv4_change_view_multiple_ptr(self):
        f_zone1 = self.zones[1]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=self.views[1],
        )
        f_zone2.save()
        r_zone = self.zones[3]

        name = "test1"
        address = "10.0.1.42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.A,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = self.views[0]
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_ipv6_add_view_to_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        r_zone = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_add_view_to_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv6_remove_view_from_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = None
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_remove_view_from_zone_old_ptr_removed(self):
        self.zones[0].delete()

        f_zone = self.zones[1]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = None
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv6_change_view_of_zone_new_ptr_added(self):
        f_zone = self.zones[1]
        self.zones[6].delete()
        r_zone = self.zones[7]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_change_view_of_zone_old_ptr_removed(self):
        f_zone = self.zones[1]
        r_zone = self.zones[6]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[1]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv6_add_view_to_ptr_zone_new_ptr_added(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = self.views[2]
        r_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_add_view_to_ptr_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = self.views[2]
        r_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv6_remove_view_from_ptr_zone_new_ptr_added(self):
        f_zone = self.zones[0]

        r_zone = self.zones[5]
        r_zone.view = self.views[2]
        r_zone.save()

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = None
        r_zone.save()

        r_record = Record.objects.get(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        self.assertEqual(r_record.value, f"{name}.{f_zone.name}.")

    def test_ipv6_remove_view_from_ptr_zone_old_ptr_removed(self):
        f_zone = self.zones[0]
        f_zone.view = self.views[2]
        f_zone.save()

        r_zone = self.zones[5]
        r_zone.view = self.views[2]
        r_zone.save()

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        r_zone.view = None
        r_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR,
                zone=r_zone,
                name=reverse_name(address, r_zone),
            )

    def test_ipv6_add_view_to_zone_no_ptr_zone(self):
        f_zone = self.zones[0]
        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        f_record = Record(
            zone=f_zone,
            name=name,
            type=RecordTypeChoices.AAAA,
            value=address,
            **self.record_data,
        )
        f_record.save()

        f_zone.view = self.views[2]
        f_zone.save()

        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(
                type=RecordTypeChoices.PTR, name=reverse_name(address, r_zone)
            )

    def test_ipv6_add_view_multiple_ptr(self):
        f_zone1 = self.zones[1]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=None,
        )
        f_zone2.save()
        r_zone = self.zones[5]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.AAAA,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = self.views[0]
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_ipv6_remove_view_multiple_ptr(self):
        f_zone1 = self.zones[0]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=self.views[1],
        )
        f_zone2.save()
        r_zone = self.zones[4]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.AAAA,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = None
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_ipv6_change_view_multiple_ptr(self):
        f_zone1 = self.zones[1]
        f_zone2 = Zone(
            name="zone2.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=self.views[1],
        )
        f_zone2.save()
        r_zone = self.zones[4]

        name = "test1"
        address = "fe80:dead:beef:1::42"

        for f_zone in (f_zone1, f_zone2):
            f_record = Record(
                zone=f_zone,
                name=name,
                type=RecordTypeChoices.AAAA,
                value=address,
                **self.record_data,
            )
            f_record.save()

        f_zone2.view = self.views[0]
        f_zone2.save()

        r_records = Record.objects.filter(
            type=RecordTypeChoices.PTR, zone=r_zone, name=reverse_name(address, r_zone)
        )

        for r_record in r_records:
            self.assertTrue(
                r_record.value
                in [f"{name}.{f_zone.name}." for f_zone in (f_zone1, f_zone2)]
            )

    def test_add_view_to_zone_zone_conflict(self):
        f_zone = self.zones[0]

        f_zone.view = self.views[0]

        with self.assertRaises(ValidationError):
            f_zone.save()

    def test_remove_view_from_zone_zone_conflict(self):
        f_zone = self.zones[1]

        f_zone.view = None

        with self.assertRaises(ValidationError):
            f_zone.save()

    def test_change_view_zone_conflict(self):
        f_zone1 = self.zones[1]

        f_zone2 = Zone(
            name="zone1.example.com",
            **self.zone_data,
            soa_mname=self.nameserver,
            view=self.views[1],
        )
        f_zone2.save()

        f_zone1.view = self.views[1]

        with self.assertRaises(ValidationError):
            f_zone1.save()

    def test_delete_view_with_zones(self):
        with self.assertRaises(IntegrityError):
            self.views[1].delete()

    def test_delete_view_without_zones(self):
        self.views[2].delete()

        self.assertEqual(View.objects.filter(name="view3").exists(), False)
