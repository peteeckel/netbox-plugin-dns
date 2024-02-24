from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase
from netbox_dns.models import View


class ViewTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = View
    brief_fields = ["description", "display", "id", "name", "url"]

    create_data = [
        {"name": "external"},
        {"name": "internal"},
        {"name": "diverse"},
    ]

    @classmethod
    def setUpTestData(cls):
        views = (
            View(name="test1"),
            View(name="test2"),
            View(name="test3"),
        )
        View.objects.bulk_create(views)
