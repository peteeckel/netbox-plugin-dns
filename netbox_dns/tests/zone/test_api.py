from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer, Registrar, Contact


class ZoneAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = Zone

    brief_fields = [
        "active",
        "description",
        "display",
        "id",
        "name",
        "rfc2317_prefix",
        "status",
        "url",
        "view",
    ]

    @classmethod
    def setUpTestData(cls):
        nameserver = NameServer.objects.create(name="ns1.example.com")

        zone_data = {
            **Zone.get_defaults(),
            "soa_mname": nameserver,
            "soa_rname": "hostmaster.example.com",
            "soa_serial_auto": False,
        }

        views = (
            View(name="view1"),
            View(name="view2"),
            View(name="view3"),
        )
        View.objects.bulk_create(views)

        registrars = (
            Registrar(name="Registrar 1"),
            Registrar(name="Registrar 2"),
        )
        Registrar.objects.bulk_create(registrars)

        contacts = (
            Contact(contact_id="contact-1"),
            Contact(contact_id="contact-2"),
            Contact(contact_id="contact-3"),
            Contact(contact_id="contact-4"),
        )
        Contact.objects.bulk_create(contacts)

        zones = (
            Zone(
                name="zone1.example.com",
                **zone_data,
                registrar=registrars[0],
                registrant=contacts[0],
                admin_c=contacts[1],
                tech_c=contacts[2],
                billing_c=contacts[3]
            ),
            Zone(name="zone2.example.com", **zone_data, registrar=registrars[0]),
            Zone(
                name="zone3.example.com",
                **zone_data,
                view=views[0],
                registrar=registrars[0],
                registrant=contacts[0],
                admin_c=contacts[0],
                tech_c=contacts[0],
                billing_c=contacts[0]
            ),
            Zone(
                name="zone4.example.com",
                **zone_data,
                view=views[1],
                registrar=registrars[1]
            ),
            Zone(name="zone5.example.com", **zone_data, view=views[2]),
        )
        for zone in zones:
            zone.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "name": "zone6.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "admin_c": contacts[1].pk,
                "tech_c": contacts[1].pk,
                "billing_c": contacts[2].pk,
            },
            {
                "name": "zone7.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone8.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "admin_c": contacts[1].pk,
                "tech_c": contacts[2].pk,
                "billing_c": contacts[3].pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "view": views[0].pk,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "view": views[1].pk,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
        ]

        cls.bulk_update_data = {
            "view": views[2].pk,
            "tags": [t.pk for t in tags],
            "registrar": registrars[1].pk,
            "registrant": contacts[3].pk,
            "admin_c": contacts[2].pk,
            "tech_c": contacts[1].pk,
            "billing_c": contacts[0].pk,
        }
