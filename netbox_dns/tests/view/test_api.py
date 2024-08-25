from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from core.models import ObjectType
from users.models import ObjectPermission
from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, NameServer, Zone


class ViewAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = View

    brief_fields = ["default_view", "description", "display", "id", "name", "url"]

    create_data = [
        {"name": "external"},
        {"name": "internal"},
        {"name": "diverse"},
    ]

    bulk_update_data = {
        "description": "Test View",
    }

    def _get_queryset(self):
        return self.model.objects.filter(default_view=False)

    @classmethod
    def setUpTestData(cls):
        cls.views = (
            View(name="test1"),
            View(name="test2"),
            View(name="test3"),
        )
        View.objects.bulk_create(cls.views)

        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }
        cls.zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="zone2.example.com", **zone_data),
            Zone(name="zone3.example.com", **zone_data),
            Zone(name="zone4.example.com", **zone_data),
        )
        for zone in cls.zones:
            zone.save()

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_list_objects_anonymous(self):
        # +
        # The standard test of the NetBox test suite fails because of the
        # default view. Override to exempt it from test.
        # -
        url = f"{self._get_list_url()}?default_view=false"

        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), self._get_queryset().count())

    def test_list_objects_brief(self):
        # +
        # The standard test of the NetBox test suite fails because of the
        # default view. Override to exempt it from test.
        # -
        self.add_permissions("netbox_dns.view_view")

        url = f"{self._get_list_url()}?brief=1&default_view=false"

        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data["results"]), self._get_queryset().count())
        self.assertEqual(sorted(response.data["results"][0]), self.brief_fields)

    def test_zones_per_view_with_permission(self):
        view = self.views[0]
        for zone in self.zones[0:3]:
            zone.view = view
            zone.save()

        self.add_permissions(
            "netbox_dns.view_view",
            "netbox_dns.view_zone",
        )

        url = reverse("plugins-api:netbox_dns-api:view-zones", kwargs={"pk": view.pk})
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

    def test_zones_per_view_without_permission(self):
        view = self.views[0]
        for zone in self.zones[0:3]:
            zone.view = view
            zone.save()

        self.add_permissions("netbox_dns.view_view")

        url = reverse("plugins-api:netbox_dns-api:view-zones", kwargs={"pk": view.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_zones = response.json()
        self.assertEqual(len(response_zones), 0)

    def test_zones_per_view_with_constrained_permission(self):
        view = self.views[0]
        for zone in self.zones[0:3]:
            zone.view = view
            zone.save()

        self.add_permissions("netbox_dns.view_view")
        object_permission = ObjectPermission(
            name="View specific zones",
            actions=["view"],
            constraints={"name__in": [zone.name for zone in self.zones[0:2]]},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Zone))
        object_permission.users.add(self.user)

        url = reverse("plugins-api:netbox_dns-api:view-zones", kwargs={"pk": view.pk})
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
