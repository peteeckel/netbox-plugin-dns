from django.urls import reverse
from rest_framework import status

from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import (
    APITestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
)
from netbox_dns.models import DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)


class DNSSECKeyTemplateAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
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
            "key_size": DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
        },
        {
            "name": "Test ZSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            "key_size": DNSSECKeyTemplateKeySizeChoices.SIZE_1024,
        },
        {
            "name": "Test CSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.ED25519,
        },
    ]

    bulk_update_data = {
        "description": "Update Description",
        "algorithm": DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256,
    }

    @classmethod
    def setUpTestData(cls):
        cls.dnssec_key_templates = (
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
        DNSSECKeyTemplate.objects.bulk_create(cls.dnssec_key_templates)

    def test_create_iso8601_lifetime(self):
        self.add_permissions("netbox_dns.add_dnsseckeytemplate")

        url = reverse("plugins-api:netbox_dns-api:dnsseckeytemplate-list")

        data = {
            "name": "Test CSK 3",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.ED25519,
            "lifetime": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        key_template = DNSSECKeyTemplate.objects.get(name="Test CSK 3")
        self.assertEqual(key_template.type, DNSSECKeyTemplateTypeChoices.TYPE_CSK)
        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED25519
        )
        self.assertEqual(key_template.lifetime, 42 * 86400)

    def test_update_iso8601_lifetime(self):
        key_template = self.dnssec_key_templates[0]

        self.add_permissions("netbox_dns.change_dnsseckeytemplate")

        url = reverse(
            "plugins-api:netbox_dns-api:dnsseckeytemplate-detail",
            kwargs={"pk": key_template.pk},
        )
        data = {
            "lifetime": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        key_template.refresh_from_db()
        self.assertEqual(key_template.lifetime, 42 * 86400)
