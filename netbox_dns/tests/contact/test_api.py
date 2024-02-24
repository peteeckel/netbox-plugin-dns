from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase
from netbox_dns.models import Contact


class ContactAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = Contact
    brief_fields = ["contact_id", "description", "display", "id", "name", "url"]

    create_data = [
        {"name": "John Doe", "contact_id": "COM-REG-JOHNDOE-42"},
        {"name": "John Doe", "contact_id": "ORG-REG-JOHNDOE-42"},
        {"name": "Jane Doe", "contact_id": "ORG-REG-JANEDOE-42"},
    ]

    @classmethod
    def setUpTestData(cls):
        contacts = (
            Contact(name="John Doe", contact_id="COM-REG-JOHNDOE-23"),
            Contact(name="John Doe", contact_id="ORG-REG-JOHNDOE-23"),
            Contact(name="Jane Doe", contact_id="COM-REG-JANEDOE-23"),
        )
        Contact.objects.bulk_create(contacts)
