from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import RegistrationContact


class RegistrationContactAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = RegistrationContact
    brief_fields = ["contact_id", "description", "display", "id", "name", "url"]

    create_data = [
        {"name": "John Doe", "contact_id": "COM-REG-JOHNDOE-42"},
        {"name": "John Doe", "contact_id": "ORG-REG-JOHNDOE-42"},
        {"name": "Jane Doe", "contact_id": "ORG-REG-JANEDOE-42"},
    ]

    bulk_update_data = {
        "name": "Paul Doe",
    }

    @classmethod
    def setUpTestData(cls):
        contacts = (
            RegistrationContact(name="John Doe", contact_id="COM-REG-JOHNDOE-23"),
            RegistrationContact(name="John Doe", contact_id="ORG-REG-JOHNDOE-23"),
            RegistrationContact(name="Jane Doe", contact_id="COM-REG-JANEDOE-23"),
        )
        RegistrationContact.objects.bulk_create(contacts)
