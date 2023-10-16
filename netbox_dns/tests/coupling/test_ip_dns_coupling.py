from django.urls import reverse
from django.test import override_settings
from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from utilities.testing import APITestCase

from extras.models import CustomField
from extras.choices import CustomFieldTypeChoices
from ipam.models import IPAddress, Prefix
from netaddr import IPNetwork
from netbox_dns.models import Record, Zone, NameServer, RecordTypeChoices


class IPAddressDNSRecordCouplingTest(APITestCase):
    network = "10.0.0.0/24"
    ns = "ns1.example.com"
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
        # Test data
        cls.nameserver = NameServer.objects.create(name=cls.ns)
        cls.zone = Zone.objects.create(
            name="zone1.example.com", **cls.zone_data, soa_mname=cls.nameserver
        )
        cls.zone2 = Zone.objects.create(
            name="zone2.example.com", **cls.zone_data, soa_mname=cls.nameserver
        )
        cls.prefix = Prefix.objects.create(prefix=cls.network)

        # Add custom fields if necessary
        ipaddress_object_type = ContentType.objects.get_for_model(IPAddress)
        zone_object_type = ContentType.objects.get_for_model(Zone)
        record_object_type = ContentType.objects.get_for_model(Record)
        try:
            cf_name = CustomField.objects.create(
                name="name",
                type=CustomFieldTypeChoices.TYPE_TEXT,
                required=False,
                group_name="DNS",
            )
            cf_name.content_types.set([ipaddress_object_type])
            cf_zone = CustomField.objects.create(
                name="zone",
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                object_type=zone_object_type,
                required=False,
                group_name="DNS",
            )
            cf_zone.content_types.set([ipaddress_object_type])
        except:
            pass

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip(self):
        zone = self.zone
        name = "test-create"
        addr = "10.0.0.25/24"

        # Grant permissions to user
        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")
        data = {"address": addr, "custom_fields": {"zone": zone.id, "name": name}}
        response = self.client.post(url, data, format="json", **self.header)

        self.assertTrue(status.is_success(response.status_code))

        # Check if "record" has been created, is managed and has correct name and zone
        ip_id = response.data["id"]
        record = Record.objects.get(ipam_ip_address=ip_id)
        self.assertEqual(record.name, name)
        self.assertEqual(record.zone.id, zone.id)
        self.assertTrue(record.managed)
        # Check value of dns_name
        ip_address = IPAddress.objects.get(id=ip_id)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_existing_dns_record(self):
        zone = self.zone
        name = "test-create-ip-existing-dns-record"
        addr = "10.0.0.25/24"

        # Create DNS record
        A = RecordTypeChoices.A
        v = str(IPNetwork(addr).ip)
        record = Record.objects.create(name=name, zone=zone, type=A, value=v)

        # Grant permissions to user
        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")
        data = {"address": addr, "custom_fields": {"zone": zone.id, "name": name}}
        response = self.client.post(url, data, format="json", **self.header)

        self.assertTrue(status.is_success(response.status_code))

        # Check if "record" has been linked to and is now managed
        ip_address = IPAddress.objects.get(id=response.data["id"])
        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertTrue(record.managed)
        self.assertEqual(record.name, name)
        self.assertEqual(record.zone, zone)
        # Check value of dns_name
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_missing_dns_permission(self):
        zone = self.zone
        name = "test-create-ip-missing-dns-perm"
        addr = "10.0.0.26/24"

        # Grant only IPAddress add permission to user,
        # and *no* DNS record add permission
        self.add_permissions("ipam.add_ipaddress")

        url = reverse("ipam-api:ipaddress-list")
        data = {"address": addr, "custom_fields": {"zone": zone.id, "name": name}}
        response = self.client.post(url, data, format="json", **self.header)

        # Should be denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # No IP address should have been created
        self.assertEqual(IPAddress.objects.filter(address=addr).count(), 0)
        # No DNS Record should have been created
        self.assertEqual(Record.objects.filter(name=name, zone_id=zone.id).count(), 0)

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip(self):
        zone = self.zone
        name = "test-delete-ip"
        addr = IPNetwork("10.0.0.27/24")
        # Grant delete on both IP address and DNS record
        self.add_permissions("ipam.delete_ipaddress")
        self.add_permissions("netbox_dns.delete_record")

        # Create DNS record and IP Address
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        record = Record.objects.create(
            name=name,
            zone=zone,
            type=A,
            value=s_addr,
            ipam_ip_address=ip_address,
        )

        # Delete address
        url = reverse("ipam-api:ipaddress-list") + str(ip_address.id) + "/"
        response = self.client.delete(url, **self.header)
        # Check response
        self.assertTrue(status.is_success(response.status_code))
        # Check if DNS record has been deleted
        self.assertEqual(Record.objects.filter(id=record.id).count(), 0)
        # Check if IP address has been deleted
        self.assertEqual(IPAddress.objects.filter(id=ip_address.id).count(), 0)

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_existing_ip(self):
        addr = IPNetwork("10.0.0.27/24")
        zone = self.zone
        name = "test-modify-name-existing-ip"
        newname = "newname"
        zone2 = self.zone2

        # Grant permissions to user
        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        # Create IP Address
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        # Create DNS record
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        record = Record.objects.create(
            name=name,
            zone=zone,
            type=A,
            value=s_addr,
            ipam_ip_address=ip_address,
        )

        # Change name and zone
        url = reverse("ipam-api:ipaddress-list") + str(ip_address.id) + "/"
        data = {"custom_fields": {"name": newname, "zone": zone2.id}}
        response = self.client.patch(url, data, format="json", **self.header)

        # Check response
        self.assertTrue(status.is_success(response.status_code))

        # Check if ip still point to a record and if record matches
        ip_address = IPAddress.objects.get(id=ip_address.id)
        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, newname)
        self.assertEqual(record_query[0].zone, zone2)
        # Check value of dns_name
        self.assertEqual(ip_address.dns_name, f"{newname}.{zone2.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_existing_ip_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.27/24")
        zone = self.zone
        name = "test-modify-name-existing-ip-no-perm"

        newname = "newname"
        zone2 = self.zone2

        # Grant permissions to user
        self.add_permissions("ipam.change_ipaddress")

        # Create IP Address
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        # Create DNS record
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        record = Record.objects.create(
            name=name,
            zone=zone,
            type=A,
            value=s_addr,
            ipam_ip_address=ip_address,
        )

        # Change name and zone
        url = reverse("ipam-api:ipaddress-list") + str(ip_address.id) + "/"
        data = {"custom_fields": {"name": newname, "zone": zone2.id}}
        response = self.client.patch(url, data, format="json", **self.header)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Check for no changes
        ip_address = IPAddress.objects.get(id=ip_address.id)
        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        # Check value of dns_name
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_existing_ip(self):
        addr = IPNetwork("10.0.0.28/24")
        zone = self.zone
        name = "test-clear-name-existing-ip"

        # Grant permissions to user
        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.delete_record")

        # Create IP Address
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        # Create DNS record
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        record = Record.objects.create(
            name=name,
            zone=zone,
            type=A,
            value=s_addr,
            ipam_ip_address=ip_address,
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.id) + "/"
        data = {"custom_fields": {"zone": None}}
        response = self.client.patch(url, data, format="json", **self.header)

        # Check response
        self.assertTrue(status.is_success(response.status_code))
        # Check if record has been deleted
        self.assertEqual(Record.objects.filter(ipam_ip_address=ip_address).count(), 0)
        # Re-read IPAddress object
        ip_address = IPAddress.objects.get(id=ip_address.id)
        # Check if dns_name is empty
        self.assertEqual(ip_address.dns_name, "")
        cf_name = ip_address.custom_field_data.get("name")
        self.assertEqual(cf_name, "")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_rename_zone_existing_ip(self):
        addr = IPNetwork("10.0.0.29/24")
        zone = self.zone
        name = "test-rename-zone-existing-ip"
        new_zone_name = "newzone.example.com"

        # Grant permissions to user
        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_zone")

        # Create IP Address
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        # Create DNS record
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        record = Record.objects.create(
            name=name,
            zone=zone,
            type=A,
            value=s_addr,
            ipam_ip_address=ip_address,
        )

        url = reverse("plugins-api:netbox_dns-api:zone-list") + str(zone.id) + "/"
        data = {"name": new_zone_name}
        response = self.client.patch(url, data, format="json", **self.header)

        # Check response
        self.assertTrue(status.is_success(response.status_code))
        # Re-read IPAddress object
        ip_address = IPAddress.objects.get(id=ip_address.id)
        # Check if dns_name has correct value
        self.assertEqual(ip_address.dns_name, f"{name}.{new_zone_name}")
        # Check if record zone has correct name
        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].zone.name, new_zone_name)

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_zone_existing_ip(self):
        addr = IPNetwork("10.0.0.30/24")
        zone = self.zone
        name = "test-delete-zone-existing-ip"

        # Create IP Address
        ip_address = IPAddress.objects.create(
            address=addr,
            dns_name=f"{name}.{zone.name}",
            custom_field_data={"name": name, "zone": zone.id},
        )
        # Create DNS record
        A = RecordTypeChoices.A
        s_addr = str(addr.ip)
        record = Record.objects.create(
            name=name, zone=zone, type=A, value=s_addr, ipam_ip_address=ip_address
        )

        # Grant permissions to user
        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.delete_zone")
        self.add_permissions("netbox_dns.delete_record")

        url = reverse("plugins-api:netbox_dns-api:zone-list") + str(zone.id) + "/"
        response = self.client.delete(url, **self.header)

        # Check response
        self.assertTrue(status.is_success(response.status_code))
        # Check if record has been deleted
        self.assertEqual(Record.objects.filter(id=record.id).count(), 0)
        # Re-read IPAddress object
        ip_address = IPAddress.objects.get(id=ip_address.id)
        # Check if dns_name is empty
        self.assertEqual(ip_address.dns_name, "")
        # Check if custom field "name" is empty
        cf_name = ip_address.custom_field_data.get("name")
        self.assertEqual(cf_name, "")
