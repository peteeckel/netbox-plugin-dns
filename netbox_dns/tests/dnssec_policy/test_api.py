from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import DNSSECPolicy
from netbox_dns.choices import DNSSECPolicyDigestChoices


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
        dnssec_policies = (
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
        DNSSECPolicy.objects.bulk_create(dnssec_policies)
