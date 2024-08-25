from django.urls import reverse
from rest_framework import status

from utilities.testing import APIViewTestCases
from core.models import ObjectType
from users.models import ObjectPermission

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import NameServer, Zone


class NameServerAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = NameServer

    brief_fields = ["description", "display", "id", "name", "url"]

    create_data = [
        {"name": "ns4.example.com"},
        {"name": "ns5.example.com"},
        {"name": "ns6.example.com"},
    ]

    bulk_update_data = {
        "description": "Test Name Server",
    }

    @classmethod
    def setUpTestData(cls):
        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns0.example.com"),
            "soa_rname": "hostmaster.example.com",
        }
        cls.zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="zone2.example.com", **zone_data),
            Zone(name="zone3.example.com", **zone_data),
            Zone(name="zone4.example.com", **zone_data),
        )

    def test_zones_per_nameserver_with_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones:
            zone.save()
        for zone in self.zones[0:3]:
            zone.nameservers.set(self.nameservers)

        self.add_permissions(
            "netbox_dns.view_nameserver",
            "netbox_dns.view_zone",
        )

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-zones", kwargs={"pk": nameserver.pk}
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 3)
        for zone in self.zones[0:3]:
            self.assertTrue(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )
        self.assertFalse(
            self.zones[3].pk
            in [response_zone.get("id") for response_zone in response_zones]
        )

    def test_zones_per_nameserver_without_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones:
            zone.save()
        for zone in self.zones[0:3]:
            zone.nameservers.set(self.nameservers)

        self.add_permissions("netbox_dns.view_nameserver")

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-zones", kwargs={"pk": nameserver.pk}
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 0)

    def test_zones_per_nameserver_with_constrained_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones:
            zone.save()
        for zone in self.zones[0:3]:
            zone.nameservers.set(self.nameservers)

        self.add_permissions("netbox_dns.view_nameserver")
        object_permission = ObjectPermission(
            name="View specific zones",
            actions=["view"],
            constraints={"name__in": [zone.name for zone in self.zones[0:2]]},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Zone))
        object_permission.users.add(self.user)

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-zones", kwargs={"pk": nameserver.pk}
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 2)
        for zone in self.zones[0:2]:
            self.assertTrue(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )
        for zone in self.zones[2:4]:
            self.assertFalse(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )

    def test_soa_zones_per_nameserver_with_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones[0:3]:
            zone.soa_mname = nameserver
            zone.save()
        self.zones[3].save()

        self.add_permissions(
            "netbox_dns.view_nameserver",
            "netbox_dns.view_zone",
        )

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-soa-zones",
            kwargs={"pk": nameserver.pk},
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 3)
        for zone in self.zones[0:3]:
            self.assertTrue(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )
        self.assertFalse(
            self.zones[3].pk
            in [response_zone.get("id") for response_zone in response_zones]
        )

    def test_soa_zones_per_nameserver_without_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones[0:3]:
            zone.soa_mname = nameserver
            zone.save()
        self.zones[3].save()

        self.add_permissions("netbox_dns.view_nameserver")

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-soa-zones",
            kwargs={"pk": nameserver.pk},
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 0)

    def test_soa_zones_per_nameserver_with_constrained_permission(self):
        nameserver = self.nameservers[0]
        for zone in self.zones[0:3]:
            zone.soa_mname = nameserver
            zone.save()
        self.zones[3].save()

        self.add_permissions("netbox_dns.view_nameserver")
        object_permission = ObjectPermission(
            name="View specific zones",
            actions=["view"],
            constraints={"name__in": [zone.name for zone in self.zones[0:2]]},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Zone))
        object_permission.users.add(self.user)

        url = reverse(
            "plugins-api:netbox_dns-api:nameserver-soa-zones",
            kwargs={"pk": nameserver.pk},
        )
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 2)
        for zone in self.zones[0:2]:
            self.assertTrue(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )
        for zone in self.zones[2:4]:
            self.assertFalse(
                zone.pk in [response_zone.get("id") for response_zone in response_zones]
            )
