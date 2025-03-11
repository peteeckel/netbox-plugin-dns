from django.urls import reverse
from rest_framework import status

from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECPolicyDigestChoices,
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
)


class DNSSECPolicyAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = DNSSECPolicy

    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "status",
        "url",
    ]

    create_data = [
        {
            "name": "Test Policy 1",
            "dnskey_ttl": 3600,
            "purge_keys": 7776000,
            "publish_safety": 3600,
            "retire_safety": 3600,
            "signatures_jitter": 43200,
            "signatures_refresh": 432000,
            "signatures_validity": 1209600,
            "signatures_validity_dnskey": 1209600,
            "max_zone_ttl": 86400,
            "zone_propagation_delay": 300,
            "create_cdnskey": True,
            "cds_digest_types": [DNSSECPolicyDigestChoices.SHA256],
            "parent_ds_ttl": 86400,
            "parent_propagation_delay": 3600,
            "use_nsec3": True,
            "nsec3_iterations": None,
            "nsec3_opt_out": False,
            "nsec3_salt_size": None,
        },
        {
            "name": "Test Policy 2",
        },
        {
            "name": "Test Policy 3",
            "max_zone_ttl": 43200,
            "create_cdnskey": True,
            "use_nsec3": False,
        },
    ]

    bulk_update_data = {
        "description": "Update Description",
        "dnskey_ttl": 7200,
        "purge_keys": 7776999,
        "publish_safety": 7200,
        "retire_safety": 7200,
        "signatures_jitter": 43299,
        "signatures_refresh": 432999,
        "signatures_validity": 1209699,
        "signatures_validity_dnskey": 1209699,
        "max_zone_ttl": 86499,
        "zone_propagation_delay": 600,
        "create_cdnskey": False,
        "cds_digest_types": [DNSSECPolicyDigestChoices.SHA384],
        "parent_ds_ttl": 86499,
        "parent_propagation_delay": 7200,
        "use_nsec3": False,
        "nsec3_iterations": 1,
        "nsec3_opt_out": True,
        "nsec3_salt_size": 32,
    }

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

        cls.dnssec_policies = (
            DNSSECPolicy(
                name="Test Policy 4",
                dnskey_ttl=3600,
                purge_keys=7776000,
                publish_safety=3600,
                retire_safety=3600,
                signatures_jitter=43200,
                signatures_refresh=432000,
                signatures_validity=1209600,
                signatures_validity_dnskey=1209600,
                max_zone_ttl=86400,
                zone_propagation_delay=300,
                create_cdnskey=True,
                cds_digest_types=[DNSSECPolicyDigestChoices.SHA256],
                parent_ds_ttl=86400,
                parent_propagation_delay=3600,
                use_nsec3=True,
                nsec3_iterations=None,
                nsec3_opt_out=False,
                nsec3_salt_size=None,
            ),
            DNSSECPolicy(
                name="Test Policy 5",
            ),
            DNSSECPolicy(
                name="Test Policy 6",
                max_zone_ttl=43200,
                create_cdnskey=True,
                use_nsec3=False,
            ),
        )
        DNSSECPolicy.objects.bulk_create(cls.dnssec_policies)

    def test_ksk_zsk(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[4]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertIn(key_template1, policy.key_templates.all())
        self.assertIn(key_template2, policy.key_templates.all())
        self.assertEqual(policy.max_zone_ttl, 424242)

    def test_csk(self):
        policy = self.dnssec_policies[0]

        key_template = self.dnssec_key_templates[0]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template.name,
                    "type": key_template.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()

        self.assertIn(key_template, policy.key_templates.all())
        self.assertEqual(policy.max_zone_ttl, 424242)

    def test_csk_ksk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[2]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_csk_zsk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[4]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_csk_csk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[0]
        key_template2 = self.dnssec_key_templates[1]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_ksk_ksk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[3]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_zsk_zsk_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[4]
        key_template2 = self.dnssec_key_templates[5]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_ksk_zsk_different_algorithm_fail(self):
        policy = self.dnssec_policies[0]

        key_template1 = self.dnssec_key_templates[2]
        key_template2 = self.dnssec_key_templates[5]

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "key_templates": [
                {
                    "name": key_template1.name,
                    "type": key_template1.type,
                },
                {
                    "name": key_template2.name,
                    "type": key_template2.type,
                },
            ],
            "max_zone_ttl": 424242,
        }

        self.add_permissions("netbox_dns.change_dnssecpolicy")
        self.add_permissions("netbox_dns.view_dnsseckeytemplate")

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        policy.refresh_from_db()

        self.assertFalse(policy.key_templates.exists())
        self.assertEqual(policy.max_zone_ttl, 86400)
