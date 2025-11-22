from django.test import TestCase

from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import RegistrationContact, NameServer, Zone
from netbox_dns.filtersets import RegistrationContactFilterSet


class RegistrationContactFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = RegistrationContact.objects.all()
    filterset = RegistrationContactFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.contacts = (
            RegistrationContact(
                name="Paul Example",
                contact_id=4242,
                organization="Example Corp.",
                street="Example Avenue",
                city="Exampletown",
                state_province="Example County",
                postal_code="04242",
                country="EX",
                phone="+49.555.424242",
                phone_ext="42",
                fax="+49.555.424242",
                fax_ext="23",
                email="paul@example.com",
            ),
            RegistrationContact(
                name="Fred Example",
                contact_id=2323,
                organization="Example Corp.",
                street="Example Avenue",
                city="Exampletown",
                state_province="Example County",
                postal_code="04242",
                country="EX",
                phone="+49.555.424242",
                phone_ext="43",
                fax="+49.555.424242",
                fax_ext="24",
                email="fred@example.com",
            ),
            RegistrationContact(
                name="Jack Example",
                contact_id=4223,
                organization="Example Trust",
                street="Example Lane",
                city="Examplingen",
                state_province="Bad Example",
                postal_code="02323",
                country="DE",
                phone="+49.6172.4242",
                phone_ext="23",
                fax="+49.6172.4242",
                fax_ext="42",
                email="jack@example.org",
            ),
        )
        RegistrationContact.objects.bulk_create(cls.contacts)

        cls.zone_data = {
            "soa_rname": "hostmaster.example.com",
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
        }

        cls.zones = (
            Zone(
                name="zone1.example.com",
                registrant=cls.contacts[0],
                admin_c=cls.contacts[1],
                tech_c=cls.contacts[1],
                billing_c=cls.contacts[0],
                **cls.zone_data,
            ),
            Zone(
                name="zone2.example.com",
                registrant=cls.contacts[0],
                admin_c=cls.contacts[2],
                tech_c=cls.contacts[2],
                billing_c=cls.contacts[0],
                **cls.zone_data,
            ),
            Zone(
                name="zone3.example.com",
                registrant=cls.contacts[0],
                admin_c=cls.contacts[2],
                tech_c=cls.contacts[2],
                billing_c=cls.contacts[0],
                **cls.zone_data,
            ),
            Zone(name="zone4.example.com", registrant=cls.contacts[2], **cls.zone_data),
        )
        for zone in cls.zones:
            zone.save()

    def test_name(self):
        params = {"name__iregex": r"(Fred|Paul) Example"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_contact_id(self):
        params = {"contact_id__iregex": r"(2323|4223|1234)"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_organization(self):
        params = {"organization": ["Example Corp."]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_street(self):
        params = {"street": ["Example Lane"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_city(self):
        params = {"city": ["Exampletown"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_state_province(self):
        params = {"state_province": ["Bad Example"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_postal_code(self):
        params = {"postal_code": ["04242", "00707"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_country(self):
        params = {"country": ["EX", "EY"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_phone(self):
        params = {"phone": ["+49.555.424242", "+49.555.1111"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"phone": ["+49.555.424242", "+49.555.1111"], "phone_ext": ["42"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_fax(self):
        params = {"fax": ["+49.555.424242", "+49.555.11111"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"fax": ["+49.555.424242", "+49.555.11111"], "fax_ext": ["32", "24"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_email(self):
        params = {"email": ["paul@example.com", "jack@example.org", "pete@acme.com"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_registrant_zone(self):
        params = {"registrant_zone_id": [self.zones[0].pk, self.zones[3].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"registrant_zone": [self.zones[0].name, self.zones[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_registrant_zone_name(self):
        params = {"registrant_zone_name": self.zones[0].name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"registrant_zone_name__iregex": r"zone[14]\..*"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_admin_c_zone(self):
        params = {"admin_c_zone_id": [self.zones[0].pk, self.zones[3].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"admin_c_zone": [self.zones[0].name, self.zones[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_admin_c_zone_name(self):
        params = {"admin_c_zone_name": self.zones[0].name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"admin_c_zone_name__iregex": r"zone[1234]\..*"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tech_c_zone(self):
        params = {"tech_c_zone_id": [self.zones[0].pk, self.zones[3].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"tech_c_zone": [self.zones[0].name, self.zones[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tech_c_zone_name(self):
        params = {"tech_c_zone_name": self.zones[0].name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"tech_c_zone_name__iregex": r"zone[1234]\..*"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_billing_c_zone(self):
        params = {"billing_c_zone_id": [self.zones[0].pk, self.zones[3].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"billing_c_zone": [self.zones[0].name, self.zones[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_billing_c_zone_name(self):
        params = {"billing_c_zone_name": self.zones[0].name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"billing_c_zone_name__iregex": r"zone[1234]\..*"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
