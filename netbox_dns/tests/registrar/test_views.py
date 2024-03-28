from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import Registrar


class RegistrarViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Registrar

    @classmethod
    def setUpTestData(cls):
        cls.registrars = [
            Registrar(
                name="ACME Corporation",
                iana_id=23,
                referral_url="https://acme.example.com",
                whois_server="whois.acme.example.com",
            ),
            Registrar(
                name="ACME Limited",
                iana_id=42,
                referral_url="https://acme.example.net",
                whois_server="whois.acme.example.net",
            ),
            Registrar(
                name="ACME Trust",
                iana_id=5,
                referral_url="https://acme.example.org",
                whois_server="whois.acme.example.org",
            ),
        ]

        Registrar.objects.bulk_create(cls.registrars)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ACME 2 Corporation",
            "iana_id": 815,
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "New Description",
            "organization": "New Organization",
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
            "name,iana_id,referral_url,whois_server",
            "ACME 3 Corporation,4223,https://acme3.example.com,whois.acme3.example.com",
            "ACME 3 Limited,2342,https://acme3.example.org,whois.acme3.example.org",
            "ACME 3 Trust,4242,https://acme3.example.net,whois.acme3.example.net",
        )

        cls.csv_update_data = (
            "id,abuse_email",
            f"{cls.registrars[0].pk},devnull@acme.example.com",
            f"{cls.registrars[1].pk},devnull@acme.example.net",
        )

    maxDiff = None
