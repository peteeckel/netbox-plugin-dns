from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import Contact


class ContactViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Contact

    @classmethod
    def setUpTestData(cls):
        cls.contacts = (
            Contact(name="John Doe", contact_id="COM-REG-JOHNDOE-23"),
            Contact(name="John Doe", contact_id="ORG-REG-JOHNDOE-23"),
            Contact(name="Jane Doe", contact_id="COM-REG-JANEDOE-23"),
        )

        Contact.objects.bulk_create(cls.contacts)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "John Doe",
            "contact_id": "COM-REG-JOHNDOE-42",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,contact_id,country,city,postal_code,email",
            "John Doe,COM-REG-JOHNDOE-42,GB,London,NW42SE,jdoe@example.com",
            "John Doe,ORG-REG-JOHNDOE-42,GB,London,NW42SE,jdoe@example.com",
            "John Doe,NET-REG-JOHNDOE-42,GB,London,NW42SE,jdoe@example.com",
            "John Doe,XXX-REG-JOHNDOE-42,GB,London,NW42SE,jdoe@example.com",
            "Jane Doe,COM-REG-JANEDOE-42,GB,London,SE42NW,janed@example.com",
            "Jane Doe,NET-REG-JANEDOE-42,GB,London,SE42NW,janed@example.com",
        )

        cls.csv_update_data = (
            "id,name,country,city,postal_code",
            f"{cls.contacts[0].pk},John Doe,IR,Dublin,IR0815",
            f"{cls.contacts[1].pk},John Doe,IR,Dublin,IR0815",
        )

        cls.bulk_edit_data = {
            "contact": cls.contacts[1].pk,
            "name": "John Doe III",
        }

    maxDiff = None
