from django.urls import reverse
from rest_framework import status

from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import (
    APITestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
)
from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate
from netbox_dns.choices import (
    DNSSECPolicyDigestChoices,
    DNSSECPolicyStatusChoices,
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
    CustomFieldTargetAPIMixin,
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
            "parental_agents": ["10.0.0.23", "2001:db8:dead:beef::23"],
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
        "parental_agents": ["10.0.0.42", "2001:db8:dead:beef::42"],
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
                parental_agents=["10.0.0.42", "2001:db8:dead:beef::23"],
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

    def test_create_iso8601_dnskey_ttl(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "dnskey_ttl": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.dnskey_ttl, 42 * 86400)

    def test_update_iso8601_dnskey_ttl(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "dnskey_ttl": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.dnskey_ttl, 42 * 86400)

    def test_create_iso8601_purge_keys(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "purge_keys": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.purge_keys, 42 * 86400)

    def test_update_iso8601_purge_keys(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "purge_keys": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.purge_keys, 42 * 86400)

    def test_create_iso8601_publish_safety(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "publish_safety": "PT42M",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.publish_safety, 42 * 60)

    def test_update_iso8601_publish_safety(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "publish_safety": "PT42M",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.publish_safety, 42 * 60)

    def test_create_iso8601_retire_safety(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "retire_safety": "PT42M",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.retire_safety, 42 * 60)

    def test_update_iso8601_retire_safety(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "retire_safety": "PT42M",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.retire_safety, 42 * 60)

    def test_create_iso8601_signatures_jitter(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "signatures_jitter": "PT7H",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.signatures_jitter, 7 * 3600)

    def test_update_iso8601_signatures_jitter(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "signatures_jitter": "PT7H",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.signatures_jitter, 7 * 3600)

    def test_create_iso8601_signatures_refresh(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "signatures_refresh": "P7D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.signatures_refresh, 7 * 86400)

    def test_update_iso8601_signatures_refresh(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "signatures_refresh": "P7D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.signatures_refresh, 7 * 86400)

    def test_create_iso8601_signatures_validity(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "signatures_validity": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.signatures_validity, 42 * 86400)

    def test_update_iso8601_signatures_validity(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "signatures_validity": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.signatures_validity, 42 * 86400)

    def test_create_iso8601_signatures_validity_dnskey(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "signatures_validity_dnskey": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.signatures_validity_dnskey, 42 * 86400)

    def test_update_iso8601_signatures_validity_dnskey(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "signatures_validity_dnskey": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.signatures_validity_dnskey, 42 * 86400)

    def test_create_iso8601_max_zone_ttl(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "max_zone_ttl": "PT24H",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_update_iso8601_max_zone_ttl(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "max_zone_ttl": "PT24H",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.max_zone_ttl, 86400)

    def test_create_iso8601_zone_propagation_delay(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "zone_propagation_delay": "PT42S",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.zone_propagation_delay, 42)

    def test_update_iso8601_zone_propagation_delay(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "zone_propagation_delay": "PT42S",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.zone_propagation_delay, 42)

    def test_create_iso8601_parent_propagation_delay(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "parent_propagation_delay": "PT42S",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.parent_propagation_delay, 42)

    def test_update_iso8601_parent_propagation_delay(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "parent_propagation_delay": "PT42S",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.parent_propagation_delay, 42)

    def test_create_iso8601_parent_ds_ttl(self):
        self.add_permissions("netbox_dns.add_dnssecpolicy")

        url = reverse("plugins-api:netbox_dns-api:dnssecpolicy-list")

        data = {
            "name": "Test Policy 7",
            "status": DNSSECPolicyStatusChoices.STATUS_ACTIVE,
            "parent_ds_ttl": "P42D",
        }

        response = self.client.post(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        policy = DNSSECPolicy.objects.get(name="Test Policy 7")
        self.assertEqual(policy.status, DNSSECPolicyStatusChoices.STATUS_ACTIVE)
        self.assertEqual(policy.parent_ds_ttl, 42 * 86400)

    def test_update_iso8601_parent_ds_ttl(self):
        policy = self.dnssec_policies[0]

        self.add_permissions("netbox_dns.change_dnssecpolicy")

        url = reverse(
            "plugins-api:netbox_dns-api:dnssecpolicy-detail", kwargs={"pk": policy.pk}
        )

        data = {
            "parent_ds_ttl": "P42D",
        }

        response = self.client.patch(url, data, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        policy.refresh_from_db()
        self.assertEqual(policy.parent_ds_ttl, 42 * 86400)
