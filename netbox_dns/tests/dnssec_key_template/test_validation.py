from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)


class DNSSECPolicyValidationTestCase(TestCase):
    def test_create_rsa_with_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(
            key_template.key_size, DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        )

    def test_create_rsa_no_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(key_template.key_size, None)

    def test_create_rsa_illegal_key_size(self):
        with self.assertRaises(ValidationError):
            DNSSECKeyTemplate.objects.create(
                name="test-template",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
                key_size=42,
            )

    def test_update_rsa_add_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(key_template.key_size, None)

        key_template.key_size = DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        key_template.save()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(
            key_template.key_size, DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        )

    def test_update_rsa_remove_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(
            key_template.key_size, DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        )

        key_template.key_size = None
        key_template.save()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(key_template.key_size, None)

    def test_update_rsa_set_illegal_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(
            key_template.key_size, DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        )

        key_template.key_size = 42
        with self.assertRaises(ValidationError):
            key_template.save()

        key_template.refresh_from_db()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.RSASHA256
        )
        self.assertEqual(
            key_template.key_size, DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        )

    def test_create_edsa256_no_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256
        )
        self.assertIsNone(key_template.key_size)

    def test_create_edsa384_no_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384
        )
        self.assertIsNone(key_template.key_size)

    def test_create_ed25519_no_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED25519
        )
        self.assertIsNone(key_template.key_size)

    def test_create_ed448_no_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ED448,
        )

        self.assertEqual(
            key_template.algorithm,
            DNSSECKeyTemplateAlgorithmChoices.ED448,
        )
        self.assertIsNone(key_template.key_size)

    def test_create_edsa256_with_key_size(self):
        with self.assertRaises(ValidationError):
            DNSSECKeyTemplate.objects.create(
                name="test-template",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256,
                key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
            )

    def test_create_edsa384_with_key_size(self):
        with self.assertRaises(ValidationError):
            DNSSECKeyTemplate.objects.create(
                name="test-template",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384,
                key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
            )

    def test_create_ed25519_with_key_size(self):
        with self.assertRaises(ValidationError):
            DNSSECKeyTemplate.objects.create(
                name="test-template",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
                key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
            )

    def test_create_ed448_with_key_size(self):
        with self.assertRaises(ValidationError):
            DNSSECKeyTemplate.objects.create(
                name="test-template",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED448,
                key_size=DNSSECKeyTemplateKeySizeChoices.SIZE_2048,
            )

    def test_update_edsa256_set_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256
        )
        self.assertEqual(key_template.key_size, None)

        key_template.key_size = DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        with self.assertRaises(ValidationError):
            key_template.save()

        key_template.refresh_from_db()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP256SHA256
        )
        self.assertEqual(key_template.key_size, None)

    def test_update_edsa384_set_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384
        )
        self.assertEqual(key_template.key_size, None)

        key_template.key_size = DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        with self.assertRaises(ValidationError):
            key_template.save()

        key_template.refresh_from_db()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ECDSAP384SHA384
        )
        self.assertEqual(key_template.key_size, None)

    def test_update_ed25519_set_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED25519
        )
        self.assertEqual(key_template.key_size, None)

        key_template.key_size = DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        with self.assertRaises(ValidationError):
            key_template.save()

        key_template.refresh_from_db()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED25519
        )
        self.assertEqual(key_template.key_size, None)

    def test_update_ed448_set_key_size(self):
        key_template = DNSSECKeyTemplate.objects.create(
            name="test-template",
            type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            algorithm=DNSSECKeyTemplateAlgorithmChoices.ED448,
        )

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED448
        )
        self.assertEqual(key_template.key_size, None)

        key_template.key_size = DNSSECKeyTemplateKeySizeChoices.SIZE_2048
        with self.assertRaises(ValidationError):
            key_template.save()

        key_template.refresh_from_db()

        self.assertEqual(
            key_template.algorithm, DNSSECKeyTemplateAlgorithmChoices.ED448
        )
        self.assertEqual(key_template.key_size, None)
