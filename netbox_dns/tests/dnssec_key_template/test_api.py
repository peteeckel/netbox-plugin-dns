from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
)


class DNSSECKeyTemplateAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = DNSSECKeyTemplate

    brief_fields = [
        "algorithm",
        "description",
        "display",
        "id",
        "key_size",
        "lifetime",
        "name",
        "type",
        "url",
    ]

    create_data = [
        {
            "name": "Test KSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_KSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            "key_size": 2048,
        },
        {
            "name": "Test ZSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            "key_size": 1024,
        },
        {
            "name": "Test CSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.ED25519,
            "key_size": 1024,
        },
    ]

    bulk_update_data = {
        "description": "Update Description",
        "algorithm": DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256,
    }

    @classmethod
    def setUpTestData(cls):
        dnssec_key_templates = (
            DNSSECKeyTemplate(
                name="Test KSK 2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="Test ZSK 2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="Test CSK 2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
        )
        DNSSECKeyTemplate.objects.bulk_create(dnssec_key_templates)
