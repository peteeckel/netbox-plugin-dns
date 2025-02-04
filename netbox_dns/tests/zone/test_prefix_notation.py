from rest_framework import status

from utilities.testing import post_data

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import (
    View,
    Zone,
    NameServer,
)
from netbox_dns.choices import ZoneStatusChoices


class ZonePrefixNotationTestCase(ModelViewTestCase):
    model = Zone

    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

        cls.zone_form_data = {
            "view": View.get_default_view().pk,
            "status": ZoneStatusChoices.STATUS_ACTIVE,
            **Zone.get_defaults(),
            "soa_serial_auto": False,
            "soa_mname": cls.nameserver.pk,
            "soa_rname": "hostmaster.example.com",
        }

    def test_create_ipv4_reverse_zone(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "10.0.42.0/24",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_302_FOUND)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 1)
        zone = zones.first()

        self.assertEqual(zone.name, "42.0.10.in-addr.arpa")

    def test_create_ipv4_reverse_zone_invalid_prefix(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "10.0.42.0/25",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 0)

    def test_create_ipv4_reverse_zone_ip_address(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "10.0.42.23",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 0)

    def test_create_ipv6_reverse_zone(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "2001:db8:42::/64",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_302_FOUND)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 1)
        zone = zones.first()

        self.assertEqual(zone.name, "0.0.0.0.2.4.0.0.8.b.d.0.1.0.0.2.ip6.arpa")

    def test_create_ipv6_reverse_zone_invalid_prefix(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "2001:db8:42::/65",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 0)

    def test_create_ipv6_reverse_zone_ip_address(self):
        self.add_permissions(
            "netbox_dns.add_zone",
            "netbox_dns.view_view",
            "netbox_dns.view_nameserver",
        )

        request_data = {
            "name": "2001:db8:42::",
            **self.zone_form_data,
        }
        request = {
            "path": self._get_url("add"),
            "data": post_data(request_data),
        }

        response = self.client.post(**request)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        zones = Zone.objects.all()
        self.assertEqual(zones.count(), 0)
