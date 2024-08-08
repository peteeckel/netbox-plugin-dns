from netaddr import IPNetwork

from django.urls import reverse
from django.core import management
from rest_framework import status

from utilities.testing import APITestCase

from ipam.models import Prefix, IPAddress, VRF
from netbox_dns.models import (
    View,
    NameServer,
    Zone,
    Record,
)
from netbox_dns.choices import RecordStatusChoices, RecordTypeChoices


class AutoDNSIPAMAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zone_data = {
            "soa_mname": nameserver,
            "soa_rname": "hostmaster.example.com",
        }

        cls.views = (
            View(name="view1"),
            View(name="view2"),
            View(name="view3"),
        )
        View.objects.bulk_create(cls.views)

        cls.zones = (
            Zone(name="zone1.example.com", view=cls.views[0], **cls.zone_data),
            Zone(name="zone2.example.com", view=cls.views[0], **cls.zone_data),
            Zone(name="example.com", view=cls.views[0], **cls.zone_data),
            Zone(name="zone1.example.com", view=cls.views[1], **cls.zone_data),
            Zone(name="zone2.example.com", view=cls.views[1], **cls.zone_data),
            Zone(name="example.com", view=cls.views[1], **cls.zone_data),
        )
        for zone in cls.zones:
            zone.save()

        cls.vrfs = (
            VRF(name="vrf1"),
            VRF(name="vrf2"),
        )
        VRF.objects.bulk_create(cls.vrfs)

        cls.prefixes = (
            Prefix(prefix="2001:db8::/48"),
            Prefix(prefix="2001:db8:1::/48"),
            Prefix(prefix="2001:db8:2::/48"),
            Prefix(prefix="2001:db8::/32"),
            Prefix(prefix="2001:db8::/48", vrf=cls.vrfs[0]),
            Prefix(prefix="2001:db8:1::/48", vrf=cls.vrfs[0]),
            Prefix(prefix="2001:db8:2::/48", vrf=cls.vrfs[0]),
            Prefix(prefix="2001:db8::/32", vrf=cls.vrfs[0]),
        )
        Prefix.objects.bulk_create(cls.prefixes)

        management.call_command("setup_autodns", verbosity=0)

    def test_create_ipaddress(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        self.add_permissions("ipam.add_ipaddress")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone)

    def test_create_ipaddress_ttl(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
            "custom_fields": {
                "ipaddress_dns_record_ttl": 86400,
            },
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.ttl, 86400)

    def test_create_ipaddress_no_ptr(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
            "custom_fields": {
                "ipaddress_dns_record_disable_ptr": True,
            },
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.disable_ptr, True)

    def test_create_ipaddress_no_dns(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        self.add_permissions("ipam.add_ipaddress")
        self.add_permissions("netbox_dns.add_record")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
            "custom_fields": {
                "ipaddress_dns_disabled": True,
            },
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        ip_address = IPAddress.objects.get(dns_name=name)
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())
        self.assertFalse(ip_address.netbox_dns_records.exists())

    def test_create_ipaddress_duplicate_record(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        Record.objects.create(
            name="name1",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value=address.split("/")[0],
        )

        self.add_permissions("ipam.add_ipaddress")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(IPAddress.objects.filter(dns_name=name).exists())
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, managed=True).exists()
        )

    def test_create_ipaddress_invalid_record(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        Record.objects.create(
            name="name1", zone=zone, type=RecordTypeChoices.CNAME, value="@"
        )

        self.add_permissions("ipam.add_ipaddress")

        url = reverse("ipam-api:ipaddress-list")

        data = {
            "address": address,
            "dns_name": name,
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(IPAddress.objects.filter(dns_name=name).exists())
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())

    def test_update_ipaddress_name(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name1 = "name1.zone1.example.com"
        name2 = "name2.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address), dns_name=name1
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "dns_name": name2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name2}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone)

    def test_update_ipaddress_address(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address1 = "2001:db8::1/64"
        address2 = "2001:db8::2/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address1), dns_name=name
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "address": address2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address2.split("/")[0])
        self.assertEqual(record.zone, zone)

    def test_update_ipaddress_name_different_zone(self):
        view = self.views[0]
        zone1 = self.zones[0]
        zone2 = self.zones[1]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name1 = "name1.zone1.example.com"
        name2 = "name1.zone2.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address), dns_name=name1
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "dns_name": name2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name2}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone2)

    def test_update_ipaddress_address_different_view(self):
        view1 = self.views[0]
        view2 = self.views[1]
        zone1 = self.zones[0]
        zone2 = self.zones[3]
        prefix1 = self.prefixes[0]
        prefix2 = self.prefixes[1]

        address1 = "2001:db8::1/64"
        address2 = "2001:db8:1::1/64"
        name = "name1.zone1.example.com"

        view1.prefixes.add(prefix1)
        view2.prefixes.add(prefix2)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address1), dns_name=name
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address1.split("/")[0])
        self.assertEqual(record.zone, zone1)

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "address": address2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address2.split("/")[0])
        self.assertEqual(record.zone, zone2)

    def test_update_ipaddress_address_no_view(self):
        view1 = self.views[0]
        view2 = self.views[2]
        zone1 = self.zones[0]
        zone2 = self.zones[3]
        prefix1 = self.prefixes[0]
        prefix2 = self.prefixes[1]

        address1 = "2001:db8::1/64"
        address2 = "2001:db8:1::1/64"
        name = "name1.zone1.example.com"

        view1.prefixes.add(prefix1)
        view2.prefixes.add(prefix2)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address1), dns_name=name
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address1.split("/")[0])
        self.assertEqual(record.zone, zone1)

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "address": address2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())
        self.assertFalse(ip_address.netbox_dns_records.exists())

    def test_update_ipaddress_vrf_different_view(self):
        view1 = self.views[0]
        view2 = self.views[1]
        zone1 = self.zones[0]
        zone2 = self.zones[3]
        prefix1 = self.prefixes[0]
        prefix2 = self.prefixes[4]
        vrf = self.vrfs[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view1.prefixes.add(prefix1)
        view2.prefixes.add(prefix2)

        ip_address = IPAddress.objects.create(address=IPNetwork(address), dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone1)

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "vrf": {"name": vrf.name},
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone2)

    def test_update_ipaddress_vrf_no_view(self):
        view1 = self.views[0]
        view2 = self.views[1]
        zone1 = self.zones[0]
        zone2 = self.zones[3]
        prefix1 = self.prefixes[0]
        prefix2 = self.prefixes[4]
        vrf = self.vrfs[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view1.prefixes.add(prefix1)

        ip_address = IPAddress.objects.create(address=IPNetwork(address), dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone1)

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "vrf": {"name": vrf.name},
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.AAAA).exists())
        self.assertFalse(ip_address.netbox_dns_records.exists())

    def test_update_ipaddress_ttl(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(address=IPNetwork(address), dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.add_record")
        self.add_permissions("netbox_dns.change_record")
        self.add_permissions("netbox_dns.delete_record")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "custom_fields": {"ipaddress_dns_record_ttl": 86400},
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.ttl, 86400)

    def test_update_ipaddress_disable_ptr(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(address=IPNetwork(address), dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.add_record")
        self.add_permissions("netbox_dns.change_record")
        self.add_permissions("netbox_dns.delete_record")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "custom_fields": {"ipaddress_dns_record_disable_ptr": True},
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertTrue(record.disable_ptr)

    def test_update_ipaddress_disable_autodns(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name = "name1.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(address=IPNetwork(address), dns_name=name)
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        self.add_permissions("ipam.change_ipaddress")
        self.add_permissions("netbox_dns.add_record")
        self.add_permissions("netbox_dns.change_record")
        self.add_permissions("netbox_dns.delete_record")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "custom_fields": {"ipaddress_dns_disabled": True},
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertFalse(Record.objects.filter(ipam_ip_address=ip_address).exists())

    def test_update_ipaddress_name_duplicate_record(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name1 = "name1.zone1.example.com"
        name2 = "name2.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address), dns_name=name1
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        Record.objects.create(
            name="name2",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value=address.split("/")[0],
        )

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "dns_name": name2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name1}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone)

    def test_update_ipaddress_name_invalid_record(self):
        view = self.views[0]
        zone = self.zones[0]
        prefix = self.prefixes[0]

        address = "2001:db8::1/64"
        name1 = "name1.zone1.example.com"
        name2 = "name2.zone1.example.com"

        view.prefixes.add(prefix)

        ip_address = IPAddress.objects.create(
            address=IPNetwork(address), dns_name=name1
        )
        self.assertTrue(Record.objects.filter(ipam_ip_address=ip_address).exists())

        Record.objects.create(
            name="name2", zone=zone, type=RecordTypeChoices.CNAME, value="@"
        )

        self.add_permissions("ipam.change_ipaddress")

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})

        data = {
            "dns_name": name2,
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        record = Record.objects.get(ipam_ip_address=ip_address)
        self.assertEqual(record.type, RecordTypeChoices.AAAA)
        self.assertEqual(record.fqdn, f"{name1}.")
        self.assertEqual(record.value, address.split("/")[0])
        self.assertEqual(record.zone, zone)
