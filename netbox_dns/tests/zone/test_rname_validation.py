from django.test import TestCase
from django.core.exceptions import ValidationError

from netbox_dns.models import NameServer, Zone


class RNameValidationTest(TestCase):
    zone_data = {
        "default_ttl": 86400,
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial": 1,
        "soa_serial_auto": False,
    }

    @classmethod
    def setUpTestData(cls):
        cls.nameserver = NameServer.objects.create(name="ns1.example.com")

    def test_rname_validation_ok(self):
        rnames = (
            "hostmaster.example.com",
            "hostmaster.example.com.",
        )

        for index, rname in enumerate(rnames):
            zone = Zone.objects.create(
                name=f"zone{index}.example.com",
                soa_rname=rname,
                **self.zone_data,
                soa_mname=self.nameserver,
            )
            self.assertEqual(zone.soa_rname, rname)

    def test_rname_validation_failure(self):
        rnames = (
            "hostmaster",  # Not an FQDN
            "hostmaster@example.com",  # E-Mail address not converted to FQDN
        )

        for index, rname in enumerate(rnames):
            with self.assertRaises(ValidationError):
                Zone.objects.create(
                    name=f"zone{index}.example.com",
                    soa_rname=rname,
                    **self.zone_data,
                    soa_mname=self.nameserver,
                )
