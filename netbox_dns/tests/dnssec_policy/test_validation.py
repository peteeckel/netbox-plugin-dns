from django.db import transaction
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from netbox_dns.models import DNSSECKeyTemplate, DNSSECPolicy
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
)


class DNSSECPolicyValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dnssec_key_templates = (
            DNSSECKeyTemplate(
                name="csk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="csk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
            DNSSECKeyTemplate(
                name="ksk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="ksk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
            DNSSECKeyTemplate(
                name="zsk-template1",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
            ),
            DNSSECKeyTemplate(
                name="zsk-template2",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
            ),
        )
        DNSSECKeyTemplate.objects.bulk_create(cls.dnssec_key_templates)

        cls.dnssec_policy = DNSSECPolicy.objects.create(name="policy1")

    def test_ksk_zsk(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[4]

        policy.key_templates.set((key_template1, key_template2))

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertIn(key_template2, policy.key_templates.all())

    def test_csk(self):
        policy = self.dnssec_policy

        key_template = self.dnssec_key_templates[0]

        policy.key_templates.set((key_template,))

        self.assertIn(key_template, policy.key_templates.all())

    def test_csk_ksk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[2]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_csk_add_ksk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[2]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_ksk_add_csk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[0]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_csk_zsk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[4]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_csk_add_zsk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[4]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_zsk_add_csk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[4]
        key_template2 = self.dnssec_key_templates[0]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_csk_csk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[1]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_csk_add_csk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[1]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_ksk_ksk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[3]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_ksk_add_ksk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[3]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_zsk_zsk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[4]
        key_template2 = self.dnssec_key_templates[5]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_zsk_add_zsk_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[4]
        key_template2 = self.dnssec_key_templates[5]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_ksk_zsk_different_algorithm_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[5]

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.set((key_template1, key_template2))

        self.assertFalse(policy.key_templates.exists())

    def test_ksk_add_zsk_different_algorithm_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[5]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())

    def test_zsk_add_ksk_different_algorithm_fail(self):
        policy = self.dnssec_policy

        key_template1 = self.dnssec_key_templates[5]
        key_template2 = self.dnssec_key_templates[2]

        policy.key_templates.set((key_template1,))
        self.assertIn(key_template1, policy.key_templates.all())

        with transaction.atomic():
            with self.assertRaises(ValidationError):
                policy.key_templates.add(key_template2)

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertNotIn(key_template2, policy.key_templates.all())
