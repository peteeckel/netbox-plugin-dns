from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone


class ZoneRNameValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

    def test_rname_validation_ok(self):
        rnames = (
            "hostmaster.example.com",
            "hostmaster.example.com.",
            r"host\.master.example.com",
            r"host\.master.example.com.",
        )

        for index, rname in enumerate(rnames):
            zone = Zone.objects.create(
                name=f"zone{index}.example.com",
                soa_rname=rname,
                soa_mname=self.nameserver,
            )
            self.assertEqual(zone.soa_rname, rname)

    def test_rname_validation_failure(self):
        rnames = (
            "hostmaster",  # Not an FQDN
            "hostmaster@example.com",  # E-Mail address not converted to FQDN
            r"host\.master.example",  # Too few zone labels after mailbox name
        )

        for index, rname in enumerate(rnames):
            with self.assertRaises(ValidationError):
                Zone.objects.create(
                    name=f"zone{index}.example.com",
                    soa_rname=rname,
                    soa_mname=self.nameserver,
                )
