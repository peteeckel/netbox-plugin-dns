from django.test import TestCase

from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import Registrar, NameServer, Zone
from netbox_dns.filtersets import RegistrarFilterSet


class RegistrarFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Registrar.objects.all()
    filterset = RegistrarFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.registrars = (
            Registrar(
                name="ACME 2 Corporation",
                iana_id=4242,
                referral_url="https://acme.com",
                whois_server="whois.acme.com",
                address="42 Corp Street, Exampletown",
                abuse_email="abuse@acme.com",
                abuse_phone="+49.555.4242",
            ),
            Registrar(
                name="ACME 2 Limited",
                iana_id=2323,
                referral_url="https://acme.com",
                whois_server="whois.acme.com",
                address="23 Limited Lane, Exampletown",
                abuse_email="abuse@acme.com",
                abuse_phone="+49.555.2323",
            ),
            Registrar(
                name="ACME 2 Trust",
                iana_id=55,
                referral_url="https://acme.org",
                whois_server="whois.acme.org",
                address="55 Trust Street, Exampletown",
                abuse_email="abuse@acme.org",
                abuse_phone="+49.555.5555",
            ),
        )
        Registrar.objects.bulk_create(cls.registrars)

        cls.zone_data = {
            "soa_rname": "hostmaster.example.com",
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
        }

        cls.zones = (
            Zone(
                name="zone1.example.com", registrar=cls.registrars[0], **cls.zone_data
            ),
            Zone(
                name="zone2.example.com", registrar=cls.registrars[0], **cls.zone_data
            ),
            Zone(
                name="zone3.example.com", registrar=cls.registrars[1], **cls.zone_data
            ),
        )
        for zone in cls.zones:
            zone.save()

    def test_name(self):
        params = {"name__iregex": r"ACME 2 (Corporation|Trust)"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_iana_id(self):
        params = {"iana_id": [2323, 4242, 1234]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_referral_url(self):
        params = {"referral_url": ["https://acme.org"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_whois_server(self):
        params = {"whois_server": ["whois.acme.com"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_address(self):
        params = {
            "address": ["23 Limited Lane, Exampletown", "007 Bond Street, Exampletown"]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_abuse_email(self):
        params = {"abuse_email": ["abuse@acme.org", "abuse@acme.com"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_abuse_phone(self):
        params = {"abuse_phone": ["+49.555.5555", "+49.555.1111"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_zone(self):
        params = {"zone_id": [self.zones[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"zone": [self.zones[1].name, self.zones[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_zone_name(self):
        params = {"zone_name": self.zones[1].name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"zone_name__iregex": r"zone[123]\.example\.com"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
