from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import DNSSECPolicy
from netbox_dns.choices import (
    DNSSECPolicyDigestChoices,
)


class DNSSECPolicyViewTestCase(
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
    model = DNSSECPolicy

    @classmethod
    def setUpTestData(cls):
        cls.dnssec_policies = (
            DNSSECPolicy(
                name="Test Policy 4",
                inline_signing=True,
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
                inline_signing=True,
                max_zone_ttl=43200,
                create_cdnskey=True,
                use_nsec3=False,
            ),
        )
        DNSSECPolicy.objects.bulk_create(cls.dnssec_policies)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Test Policy 1",
            "inline_signing": True,
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
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "Update Description",
            "inline_signing": False,
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

        cls.csv_data = (
            "name,inline_signing,dnskey_ttl,max_zone_ttl,create_cdnskey,use_nsec3",
            f"Test Policy 1,true,86400,43200,true,true",
            f"Test Policy 2,false,86400,43200,false,true",
            f"Test Policy 3,true,43200,86400,true,false",
        )

        cls.csv_update_data = (
            "id,description,use_nsec3,create_cdnskey,inline_signing",
            f"{cls.dnssec_policies[0].pk},Test Description 1,true,true,true",
            f"{cls.dnssec_policies[1].pk},Test Description 2,false,false,false",
        )

    maxDiff = None
