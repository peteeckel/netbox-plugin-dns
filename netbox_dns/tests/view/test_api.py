from django.test import override_settings
from rest_framework import status

from ipam.models import Prefix
from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View


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

    def _get_queryset(self):
        return self.model.objects.filter(default_view=False)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"])
    def test_list_objects_anonymous(self):
        url = f"{self._get_list_url()}?default_view=false"

        response = self.client.get(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), self._get_queryset().count())

    def test_list_objects_brief(self):
        self.add_permissions(
            f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"
        )
        url = f"{self._get_list_url()}?brief=1&default_view=false"

        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data["results"]), self._get_queryset().count())
        self.assertEqual(sorted(response.data["results"][0]), self.brief_fields)

    @classmethod
    def setUpTestData(cls):
        views = (
            View(name="test1"),
            View(name="test2"),
            View(name="test3"),
        )
        View.objects.bulk_create(views)

        prefixes = (
            Prefix(prefix="10.13.1.0/24"),
            Prefix(prefix="10.23.1.0/24"),
            Prefix(prefix="10.37.1.0/24"),
            Prefix(prefix="10.42.1.0/24"),
        )
        Prefix.objects.bulk_create(prefixes)

        cls.create_data = [
            {"name": "external", "prefixes": [prefixes[0].pk, prefixes[1].pk]},
            {"name": "internal", "prefixes": [prefixes[2].pk]},
            {"name": "diverse"},
        ]

        cls.bulk_update_data = {
            "description": "Test View",
            "prefixes": [prefixes[0].pk, prefixes[1].pk],
        }
