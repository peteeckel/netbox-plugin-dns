from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase
from netbox_dns.models import Registrar


class RegistrarAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = Registrar

    brief_fields = ["description", "display", "iana_id", "id", "name", "url"]

    create_data = [
        {
            "name": "ACME Corporation",
            "iana_id": 42,
            "abuse_email": "devnull@acme.example.com",
        },
        {
            "name": "ACME Limited",
            "iana_id": 23,
            "abuse_email": "devnull@acme.example.net",
        },
        {"name": "ACME Trust", "iana_id": 5, "abuse_email": "devnull@acme.example.org"},
    ]

    bulk_update_data = {
        "whois_server": "whois.example.com",
        "address": "42 Drury Lane, Duloc 42523",
    }

    @classmethod
    def setUpTestData(cls):
        registrars = (
            Registrar(name="ACME 2 Corporation", iana_id=4242),
            Registrar(name="ACME 2 Limited", iana_id=2323),
            Registrar(name="ACME 2 Trust", iana_id=55),
        )
        Registrar.objects.bulk_create(registrars)
