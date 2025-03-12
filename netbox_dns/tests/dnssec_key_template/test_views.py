from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)


class DNSSECKeyTemplateViewTestCase(
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
    model = DNSSECKeyTemplate

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

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Test KSK",
            "type": DNSSECKeyTemplateTypeChoices.TYPE_KSK,
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            "key_size": DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "New Description",
            "algorithm": DNSSECKeyTemplateAlgorithmChoices.ED25519,
            "key_size": None,
        }

        cls.csv_data = (
            "name,type,algorithm,key_size",
            f"Test KSK,{DNSSECKeyTemplateTypeChoices.TYPE_KSK},{DNSSECKeyTemplateAlgorithmChoices.RSASHA256},{DNSSECKeyTemplateKeySizeChoices.SIZE_2048}",
            f"Test ZSK,{DNSSECKeyTemplateTypeChoices.TYPE_ZSK},{DNSSECKeyTemplateAlgorithmChoices.RSASHA256},{DNSSECKeyTemplateKeySizeChoices.SIZE_1024}",
            f"Test CSK,{DNSSECKeyTemplateTypeChoices.TYPE_CSK},{DNSSECKeyTemplateAlgorithmChoices.RSASHA256},{DNSSECKeyTemplateKeySizeChoices.SIZE_2048}",
        )

        cls.csv_update_data = (
            "id,description",
            f"{cls.dnssec_key_templates[0].pk},Test Description",
            f"{cls.dnssec_key_templates[1].pk},Test Description",
        )

    maxDiff = None
