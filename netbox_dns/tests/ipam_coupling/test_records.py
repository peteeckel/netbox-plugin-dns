from django.test import TestCase, override_settings
from django.core import management
from django.core.exceptions import ValidationError

from ipam.models import IPAddress
from netaddr import IPNetwork
from netbox_dns.models import Record, Zone, NameServer, RecordTypeChoices


class IPAMCouplingRecordTest(TestCase):
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
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")
        cls.zones = (
            Zone(name="zone1.example.com", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(name="zone2.example.com", **cls.zone_data, soa_mname=cls.nameserver),
            Zone(name="0.0.10.in-addr.arpa", **cls.zone_data, soa_mname=cls.nameserver),
        )
        for zone in cls.zones:
            zone.save()

        #
        # Add the required custom fields
        #
        management.call_command("setup_coupling")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip(self):
        zone = self.zones[0]
        name = "name42"
        address = IPNetwork("10.0.0.42/24")

        ip_address = IPAddress(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )
        ip_address.save()

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.name, name)
        self.assertEqual(record.zone, zone)
        self.assertTrue(record.managed)

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_existing_dns_record(self):
        zone = self.zones[0]
        name = "name42"
        address = IPNetwork("10.0.0.42/24")

        unmanaged_address_record = Record.objects.create(
            name=name,
            zone=zone,
            type=RecordTypeChoices.A,
            value=str(address.ip),
        )

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )

        managed_address_record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertTrue(managed_address_record.managed)
        self.assertEqual(managed_address_record.name, name)
        self.assertEqual(managed_address_record.zone, zone)

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

        self.assertFalse(unmanaged_address_record.managed)
        self.assertEqual(unmanaged_address_record.name, name)
        self.assertEqual(unmanaged_address_record.zone, zone)
        self.assertNotEqual(unmanaged_address_record.pk, managed_address_record.pk)

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_invalid_name(self):
        zone = self.zones[0]
        name = "aa--name42"
        address = IPNetwork("10.0.0.42/24")

        ip_address = IPAddress(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )
        with self.assertRaises(ValidationError):
            ip_address.save()

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip(self):
        zone = self.zones[0]
        name = "name23"
        address = IPNetwork("10.0.0.23/24")

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )
        address_record = ip_address.netbox_dns_records.first()
        ptr_record_id = address_record.ptr_record.id

        ip_address.delete()

        self.assertFalse(IPAddress.objects.filter(id=ip_address.id).exists())
        self.assertFalse(Record.objects.filter(id=address_record.id).exists())
        self.assertFalse(Record.objects.filter(id=ptr_record_id).exists())

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_cf(self):
        address = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name1 = "test42"
        name2 = "test23"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name1,
            },
        )

        ip_address.custom_field_data = {
            "ipaddress_dns_zone_id": zone.id,
            "ipaddress_dns_record_name": name2,
        }
        ip_address.save()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name2)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(ip_address.dns_name, f"{name2}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_zone_cf(self):
        address = IPNetwork("10.0.0.42/24")
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        name = "test42"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone1.id,
                "ipaddress_dns_record_name": name,
            },
        )

        ip_address.custom_field_data = {
            "ipaddress_dns_zone_id": zone2.id,
            "ipaddress_dns_record_name": name,
        }
        ip_address.save()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone2)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone2.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_cf(self):
        address = IPNetwork("10.0.0.27/24")
        zone = self.zones[0]
        name = "test42"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        ip_address.custom_field_data = {
            "ipaddress_dns_zone_id": zone.id,
            "ipaddress_dns_record_name": None,
        }
        ip_address.save()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())
        self.assertFalse(
            Record.objects.filter(name=name, zone=zone, managed=True).exists()
        )
        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_name": None,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_zone_cf(self):
        address = IPNetwork("10.0.0.27/24")
        zone = self.zones[0]
        name = "test42"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        ip_address.custom_field_data = {
            "ipaddress_dns_zone_id": None,
            "ipaddress_dns_record_name": name,
        }
        ip_address.save()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())
        self.assertFalse(
            Record.objects.filter(name=name, zone=zone, managed=True).exists()
        )
        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_name": None,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_rename_zone(self):
        address = IPNetwork("10.0.0.27/24")
        zone = self.zones[0]
        name = "test42"
        new_zone_name = "zone3.example.com"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )

        zone.name = new_zone_name
        zone.save()

        ip_address.refresh_from_db()
        self.assertEqual(ip_address.dns_name, f"{name}.{new_zone_name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_zone(self):
        address = IPNetwork("10.0.0.27/24")
        zone = self.zones[0]
        name = "test42"

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_zone_id": zone.id,
                "ipaddress_dns_record_name": name,
            },
        )

        zone.delete()

        ip_address.refresh_from_db()
        self.assertEqual(ip_address.netbox_dns_records.count(), 0)
        self.assertEqual(ip_address.dns_name, f"")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_name": None,
            },
        )
