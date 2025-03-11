from django.test import TestCase

from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import DNSSECKeyTemplate, DNSSECPolicy
from netbox_dns.filtersets import DNSSECPolicyFilterSet
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECPolicyDigestChoices,
    DNSSECPolicyStatusChoices,
)


class DNSSECPolicyFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet

    ignore_fields = ("key_templates",)

    @classmethod
    def setUpTestData(cls):
        cls.dnssec_policies = (
            DNSSECPolicy(
                name="Test Policy 1",
                status=DNSSECPolicyStatusChoices.STATUS_ACTIVE,
                dnskey_ttl=3600,
                purge_keys=7776000,
                publish_safety=7200,
                retire_safety=3600,
                signatures_jitter=43200,
                signatures_refresh=432001,
                signatures_validity=1209600,
                signatures_validity_dnskey=1209601,
                max_zone_ttl=86400,
                zone_propagation_delay=300,
                create_cdnskey=True,
                cds_digest_types=[DNSSECPolicyDigestChoices.SHA256],
                parent_ds_ttl=86400,
                parent_propagation_delay=3601,
                use_nsec3=True,
                nsec3_iterations=None,
                nsec3_opt_out=False,
                nsec3_salt_size=16,
            ),
            DNSSECPolicy(
                name="Test Policy 2",
                status=DNSSECPolicyStatusChoices.STATUS_ACTIVE,
                dnskey_ttl=7200,
                purge_keys=7776000,
                publish_safety=3600,
                retire_safety=3600,
                signatures_jitter=43201,
                signatures_refresh=432000,
                signatures_validity=1209601,
                signatures_validity_dnskey=1209600,
                max_zone_ttl=86400,
                zone_propagation_delay=600,
                create_cdnskey=True,
                cds_digest_types=[DNSSECPolicyDigestChoices.SHA256],
                parent_ds_ttl=86400,
                parent_propagation_delay=3600,
                use_nsec3=False,
                nsec3_iterations=1,
                nsec3_opt_out=True,
                nsec3_salt_size=None,
            ),
            DNSSECPolicy(
                name="Test Policy 3",
                status=DNSSECPolicyStatusChoices.STATUS_INACTIVE,
                dnskey_ttl=3600,
                purge_keys=7776001,
                publish_safety=3600,
                retire_safety=3601,
                signatures_jitter=43200,
                signatures_refresh=432000,
                signatures_validity=1209600,
                signatures_validity_dnskey=1209601,
                max_zone_ttl=86401,
                zone_propagation_delay=300,
                create_cdnskey=False,
                cds_digest_types=[DNSSECPolicyDigestChoices.SHA384],
                parent_ds_ttl=86401,
                parent_propagation_delay=3600,
                use_nsec3=True,
                nsec3_iterations=2,
                nsec3_opt_out=True,
                nsec3_salt_size=None,
            ),
        )
        DNSSECPolicy.objects.bulk_create(cls.dnssec_policies)

        cls.dnssec_key_templates = (
            DNSSECKeyTemplate(
                name="Test KSK",
                type=DNSSECKeyTemplateTypeChoices.TYPE_KSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
                lifetime=86400,
            ),
            DNSSECKeyTemplate(
                name="Test ZSK",
                type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.RSASHA256,
                lifetime=86400,
                key_size=1024,
            ),
            DNSSECKeyTemplate(
                name="Test CSK",
                type=DNSSECKeyTemplateTypeChoices.TYPE_CSK,
                algorithm=DNSSECKeyTemplateAlgorithmChoices.ED25519,
                lifetime=864000,
            ),
        )
        DNSSECKeyTemplate.objects.bulk_create(cls.dnssec_key_templates)

        cls.dnssec_policies[0].key_templates.set(cls.dnssec_key_templates[0:2])
        cls.dnssec_policies[1].key_templates.set([cls.dnssec_key_templates[2]])
        cls.dnssec_policies[2].key_templates.set([cls.dnssec_key_templates[1]])

    def test_name(self):
        params = {"name": ["Test Policy 1", "Test Policy 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": [DNSSECPolicyStatusChoices.STATUS_ACTIVE]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"status": [DNSSECPolicyStatusChoices.STATUS_INACTIVE]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_dnskey_ttl(self):
        params = {"dnskey_ttl": [3600]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_purge_keys(self):
        params = {"purge_keys": [7776000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_publish_safety(self):
        params = {"publish_safety": [3600]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_retire_safety(self):
        params = {"retire_safety": [3600]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_signatures_jitter(self):
        params = {"signatures_jitter": [43200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_signatures_refresh(self):
        params = {"signatures_refresh": [432000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_signatures_validity(self):
        params = {"signatures_validity": [1209600]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_signatures_validity_dnskey(self):
        params = {"signatures_validity_dnskey": [1209600]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_max_zone_ttl(self):
        params = {"max_zone_ttl": [86400]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_zone_propagation_delay(self):
        params = {"zone_propagation_delay": [300]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_create_cdnskey(self):
        params = {"create_cdnskey": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"create_cdnskey": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_cds_digest_types(self):
        params = {"cds_digest_types": [DNSSECPolicyDigestChoices.SHA256]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cds_digest_types": [DNSSECPolicyDigestChoices.SHA384]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "cds_digest_types": [
                DNSSECPolicyDigestChoices.SHA256,
                DNSSECPolicyDigestChoices.SHA384,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_parent_ds_ttl(self):
        params = {"parent_ds_ttl": [86400]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent_propagation_delay(self):
        params = {"parent_propagation_delay": [3600, 7200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_use_nsec3(self):
        params = {"use_nsec3": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"use_nsec3": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_nsec3_opt_out(self):
        params = {"nsec3_opt_out": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"nsec3_opt_out": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_nsec3_iterations(self):
        params = {"nsec3_iterations": [1, 2, 3]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_nsec3_salt_size(self):
        params = {"nsec3_salt_size": [16, 32]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_key_templates(self):
        params = {"key_template_id": [self.dnssec_key_templates[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"key_template": [self.dnssec_key_templates[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
