from unittest import skip

from django.urls import reverse
from django.test import override_settings
from django.core import management
from core.models import ObjectType

from rest_framework import status
from utilities.testing import APITestCase

from ipam.models import IPAddress
from netaddr import IPNetwork
from netbox_dns.models import Record, Zone, NameServer
from users.models import ObjectPermission


class IPAMCouplingAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="zone2.example.com", **zone_data),
            Zone(name="0.0.10.in-addr.arpa", **zone_data),
        )
        for zone in cls.zones:
            zone.save()

        #
        # Add the required custom fields
        #
        management.call_command("setup_coupling")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_with_dns_permission(self):
        zone = self.zones[0]
        name = "name42"
        address = "10.0.0.25/24"

        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")
        data = {
            "address": address,
            "custom_fields": {
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_record_ttl": None,
            },
        }
        response = self.client.post(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(pk=response.data["id"])
        address_record = ip_address.netbox_dns_records.first()

        self.assertEqual(address_record.name, name)
        self.assertEqual(address_record.zone, zone)
        self.assertEqual(address_record.ttl, None)
        self.assertTrue(address_record.managed)

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_with_dns_permission_ttl(self):
        zone = self.zones[0]
        name = "name42"
        address = "10.0.0.25/24"

        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")
        data = {
            "address": address,
            "custom_fields": {
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_record_ttl": 4223,
            },
        }
        response = self.client.post(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(pk=response.data["id"])
        address_record = ip_address.netbox_dns_records.first()

        self.assertEqual(address_record.name, name)
        self.assertEqual(address_record.zone, zone)
        self.assertEqual(address_record.ttl, 4223)
        self.assertTrue(address_record.managed)

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_create_ip_missing_dns_permission(self):
        zone = self.zones[0]
        name = "name42"
        address = "10.0.0.42/24"

        self.add_permissions("ipam.add_ipaddress")

        url = reverse("ipam-api:ipaddress-list")
        data = {
            "address": address,
            "custom_fields": {
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_record_ttl": None,
            },
        }
        response = self.client.post(url, data, format="json", **self.header)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(IPAddress.objects.filter(address=address).exists())
        self.assertFalse(Record.objects.filter(name=name, zone_id=zone.pk).exists())

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip_with_dns_permission(self):
        zone = self.zones[0]
        name = "name23"
        address = IPNetwork("10.0.0.23/24")

        self.add_permissions("ipam.delete_ipaddress")
        self.add_permissions("netbox_dns.delete_record")

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
            },
        )
        address_record = ip_address.netbox_dns_records.first()
        ptr_record_id = address_record.ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(IPAddress.objects.filter(pk=ip_address.pk).exists())
        self.assertFalse(Record.objects.filter(pk=address_record.pk).exists())
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip_with_dns_object_permission(self):
        zone = self.zones[0]
        name = "name23"
        address = IPNetwork("10.0.0.23/24")

        self.add_permissions("ipam.delete_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record", actions=["delete"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
            },
        )
        address_record = ip_address.netbox_dns_records.first()
        ptr_record_id = address_record.ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(IPAddress.objects.filter(pk=ip_address.pk).exists())
        self.assertFalse(Record.objects.filter(pk=address_record.pk).exists())
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

    @skip("APIClient has problems handling exceptions")
    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip_missing_dns_permission(self):
        zone = self.zones[0]
        name = "name23"
        address = IPNetwork("10.0.0.23/24")

        self.add_permissions("ipam.delete_ipaddress")

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
            },
        )
        address_record = ip_address.netbox_dns_records.first()
        ptr_record_id = address_record.ptr_record_id

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)
        self.assertTrue(IPAddress.objects.filter(pk=ip_address.pk).exists())
        self.assertTrue(Record.objects.filter(pk=address_record.pk).exists())
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

    @skip("APIClient has problems handling exceptions")
    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_delete_ip_missing_dns_object_permission(self):
        zone = self.zones[0]
        name = "name23"
        address = IPNetwork("10.0.0.23/24")

        self.add_permissions("ipam.delete_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record",
            actions=["delete"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=address,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
            },
        )
        address_record = ip_address.netbox_dns_records.first()
        ptr_record_id = address_record.ptr_record_id

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)
        self.assertTrue(IPAddress.objects.filter(pk=ip_address.pk).exists())
        self.assertTrue(Record.objects.filter(pk=address_record.pk).exists())
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name1 = "name42"
        name2 = "name23"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": name2,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name2)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(ip_address.dns_name, f"{name2}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name1 = "name42"
        name2 = "name23"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record", actions=["change"], constraints={"name": name1}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": name2,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name2)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(ip_address.dns_name, f"{name2}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_zone_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": zone2.pk,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone2)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone2.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_zone_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record", actions=["change"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": zone2.pk,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone2)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone2.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name1 = "name42"
        name2 = "name23"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": name2,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name1)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(ip_address.dns_name, f"{name1}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_name_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name1 = "name42"
        name2 = "name23"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": name2,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name1)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(ip_address.dns_name, f"{name1}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name1,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_zone_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": zone2.pk,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone1)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone1.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_zone_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": zone2.pk,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone1)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone1.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone1.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.delete_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": None,
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record", actions=["delete"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": None,
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_zone_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.delete_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": None,
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_zone_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record", actions=["delete"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertFalse(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, "")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": None,
                "ipaddress_dns_zone_id": None,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_name_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record",
            actions=["delete"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_name": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_zone_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_zone_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Delete Test Record",
            actions=["delete"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )
        ptr_record_id = ip_address.netbox_dns_records.first().ptr_record.pk

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_zone_id": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(
            Record.objects.filter(ipam_ip_address=ip_address, managed=True).exists()
        )
        self.assertTrue(Record.objects.filter(pk=ptr_record_id).exists())

        ip_address.refresh_from_db()

        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_ttl_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 2342)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_add_ttl_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 2342)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_remove_ttl_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, None)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_add_ttl_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, None)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_add_ttl_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, None)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": None,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_ttl_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_modify_ttl_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": 2342,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_remove_ttl_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_remove_ttl_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Modify Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_ttl": None,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
        self.assertEqual(
            ip_address.custom_field_data,
            {
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_set_disable_ptr_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": True,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertTrue(record_query[0].disable_ptr)
        self.assertIsNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_disable_ptr_with_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.change_record")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": True,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": False,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertFalse(record_query[0].disable_ptr)
        self.assertIsNotNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_set_disable_ptr_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Change Test Record", actions=["change"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": True,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertTrue(record_query[0].disable_ptr)
        self.assertIsNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_disable_ptr_with_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Change Test Record", actions=["change"], constraints={"name": name}
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": True,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": False,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertFalse(record_query[0].disable_ptr)
        self.assertIsNotNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_set_disable_ptr_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": True,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertFalse(record_query[0].disable_ptr)
        self.assertIsNotNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_disable_ptr_missing_dns_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": True,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": False,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertTrue(record_query[0].disable_ptr)
        self.assertIsNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_set_disable_ptr_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Change Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": False,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": True,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertFalse(record_query[0].disable_ptr)
        self.assertIsNotNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")

    @override_settings(PLUGINS_CONFIG={"netbox_dns": {"feature_ipam_coupling": True}})
    def test_clear_disable_ptr_missing_dns_object_permission(self):
        addr = IPNetwork("10.0.0.42/24")
        zone = self.zones[0]
        name = "name42"

        self.add_permissions("ipam.change_ipaddress")

        object_permission = ObjectPermission(
            name="Change Test Record",
            actions=["change"],
            constraints={"name": "whatever"},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        ip_address = IPAddress.objects.create(
            address=addr,
            custom_field_data={
                "ipaddress_dns_record_name": name,
                "ipaddress_dns_zone_id": zone.pk,
                "ipaddress_dns_record_ttl": 4223,
                "ipaddress_dns_record_disable_ptr": True,
            },
        )

        url = reverse("ipam-api:ipaddress-list") + str(ip_address.pk) + "/"
        data = {
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": False,
            }
        }
        response = self.client.patch(url, data, format="json", **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        ip_address.refresh_from_db()

        record_query = Record.objects.filter(ipam_ip_address=ip_address)
        self.assertEqual(record_query.count(), 1)
        self.assertEqual(record_query[0].name, name)
        self.assertEqual(record_query[0].zone, zone)
        self.assertEqual(record_query[0].ttl, 4223)
        self.assertTrue(record_query[0].disable_ptr)
        self.assertIsNone(record_query[0].ptr_record)
        self.assertEqual(ip_address.dns_name, f"{name}.{zone.name}")
