from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer, Registrar, RegistrationContact
from netbox_dns.choices import ZoneStatusChoices, ZoneEPPStatusChoices


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
    user_permissions = [
        "netbox_dns.view_view",
        "netbox_dns.view_nameserver",
    ]

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

        zone_data = {
            **Zone.get_defaults(),
            "soa_mname": nameservers[0],
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
            RegistrationContact(contact_id="contact-1"),
            RegistrationContact(contact_id="contact-2"),
            RegistrationContact(contact_id="contact-3"),
            RegistrationContact(contact_id="contact-4"),
        )
        RegistrationContact.objects.bulk_create(contacts)

        zones = (
            Zone(
                name="zone1.example.com",
                **zone_data,
                registrar=registrars[0],
                registrant=contacts[0],
                admin_c=contacts[1],
                tech_c=contacts[2],
                billing_c=contacts[3],
                domain_status=ZoneEPPStatusChoices.EPP_STATUS_CLIENT_TRANSFER_PROHIBITED,
                expiration_date="2025-04-01",
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
                billing_c=contacts[0],
            ),
            Zone(
                name="zone4.example.com",
                **zone_data,
                view=views[1],
                registrar=registrars[1],
            ),
            Zone(name="zone5.example.com", **zone_data, view=views[2]),
        )
        for zone in zones:
            zone.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "name": "zone6.example.com",
                "status": ZoneStatusChoices.STATUS_RESERVED,
                "nameservers": [nameserver.pk for nameserver in nameservers[0:2]],
                **zone_data,
                "soa_mname": nameservers[0].pk,
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "admin_c": contacts[1].pk,
                "tech_c": contacts[1].pk,
                "billing_c": contacts[2].pk,
            },
            {
                "name": "zone7.example.com",
                "status": ZoneStatusChoices.STATUS_RESERVED,
                "nameservers": [nameserver.pk for nameserver in nameservers[1:3]],
                **zone_data,
                "soa_mname": nameservers[0].pk,
            },
            {
                "name": "zone8.example.com",
                "status": ZoneStatusChoices.STATUS_RESERVED,
                "nameservers": [nameserver.pk for nameserver in nameservers[0:3]],
                **zone_data,
                "soa_mname": nameservers[0].pk,
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "admin_c": contacts[1].pk,
                "tech_c": contacts[2].pk,
                "billing_c": contacts[3].pk,
            },
            {
                "name": "zone9.example.com",
                "nameservers": [nameservers[0].pk],
                **zone_data,
                "view": views[0].pk,
                "soa_mname": nameservers[0].pk,
            },
            {
                "name": "zone9.example.com",
                "nameservers": [nameservers[0].pk, nameservers[1].pk],
                **zone_data,
                "view": views[1].pk,
                "soa_mname": nameservers[0].pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "soa_mname": nameservers[0].pk,
            },
        ]

        cls.bulk_update_data = {
            "view": views[2].pk,
            "tags": [t.pk for t in tags],
            "nameservers": [nameserver.pk for nameserver in nameservers],
            "registrar": registrars[1].pk,
            "registrant": contacts[3].pk,
            "admin_c": contacts[2].pk,
            "tech_c": contacts[1].pk,
            "billing_c": contacts[0].pk,
        }
