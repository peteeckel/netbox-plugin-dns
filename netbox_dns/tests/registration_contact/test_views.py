from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import RegistrationContact, NameServer, Zone


class RegistrationContactViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = RegistrationContact

    @classmethod
    def setUpTestData(cls):
        cls.contacts = (
            RegistrationContact(name="John Doe", contact_id="COM-REG-JOHNDOE-23"),
            RegistrationContact(name="John Doe", contact_id="ORG-REG-JOHNDOE-23"),
            RegistrationContact(name="Jane Doe", contact_id="COM-REG-JANEDOE-23"),
        )

        RegistrationContact.objects.bulk_create(cls.contacts)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "John Doe",
            "contact_id": "COM-REG-JOHNDOE-42",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "name": "New Name",
            "description": "New Description",
            "organization": "New Organization",
            "street": "New Street",
            "city": "New City",
            "state_province": "New State",
            "postal_code": "42",
            "country": "XX",
            "phone": "0815-424242",
            "phone_ext": "42",
            "fax": "0815-232323",
            "fax_ext": "23",
            "email": "no-reply@example.com",
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

    maxDiff = None

    def test_zones_viewtab(self):
        contact = self.contacts[0]

        nameserver = NameServer.objects.create(name="ns1.example.com")
        Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
            registrant=contact,
        )

        self.add_permissions(
            "netbox_dns.view_registrationcontact",
        )

        request = {
            "path": self._get_url("zones", instance=contact),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)
