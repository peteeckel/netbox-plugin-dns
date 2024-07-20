from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import RecordTemplate
from netbox_dns.choices import RecordTypeChoices


class RecordTemplateAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = RecordTemplate
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "record_name",
        "status",
        "ttl",
        "type",
        "url",
        "value",
    ]

    @classmethod
    def setUpTestData(cls):
        record_templates = (
            RecordTemplate(
                type=RecordTypeChoices.A,
                name="A record example1",
                record_name="example1",
                value="192.168.1.1",
                ttl=5000,
            ),
            RecordTemplate(
                type=RecordTypeChoices.AAAA,
                name="AAAA record example2",
                record_name="example2",
                value="fe80::dead:beef",
                disable_ptr=True,
                ttl=6000,
            ),
            RecordTemplate(
                type=RecordTypeChoices.TXT,
                name="TXT record example3",
                record_name="example3",
                value="TXT Record",
                ttl=7000,
            ),
            RecordTemplate(
                type=RecordTypeChoices.CNAME,
                name="CNAME record example4",
                record_name="example4",
                value="relative.link",
                ttl=5000,
            ),
            RecordTemplate(
                type=RecordTypeChoices.CNAME,
                name="CNAME record example5",
                record_name="example5",
                value="absolute.link.example.com.",
                ttl=5000,
            ),
        )
        RecordTemplate.objects.bulk_create(record_templates)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "type": RecordTypeChoices.A,
                "name": "A record example6",
                "record_name": "example6",
                "value": "1.1.1.1",
                "ttl": 9600,
            },
            {
                "type": RecordTypeChoices.AAAA,
                "name": "AAAA record example7",
                "record_name": "example7",
                "value": "fe80::dead:beef",
                "disable_ptr": True,
                "ttl": 9600,
            },
            {
                "type": RecordTypeChoices.TXT,
                "name": "TXT record example8",
                "record_name": "example8",
                "value": "TXT Record",
                "ttl": 9600,
            },
            {
                "type": RecordTypeChoices.CNAME,
                "name": "CNAME record example9",
                "record_name": "example9",
                "value": "relative.link",
                "ttl": 9600,
            },
            {
                "type": RecordTypeChoices.CNAME,
                "name": "CNAME record example10",
                "record_name": "example10",
                "value": "absolute.link.example.com.",
                "ttl": 9600,
            },
        ]

        cls.bulk_update_data = {
            "ttl": 19200,
            "tags": [t.pk for t in tags],
        }
