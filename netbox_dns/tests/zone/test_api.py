from django.urls import reverse
from rest_framework import status

from utilities.testing import APIViewTestCases, create_tags
from core.models import ObjectType
from users.models import ObjectPermission

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer, Registrar, Contact, Record
from netbox_dns.choices import RecordTypeChoices


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
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

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

        zone_data = {
            **Zone.get_defaults(),
            "soa_mname": nameservers[0],
            "soa_rname": "hostmaster.example.com",
            "soa_serial_auto": False,
        }
        cls.zones = (
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
        for zone in cls.zones:
            zone.save()

        cls.records = (
            Record(
                name="name1",
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
            ),
            Record(
                name="name2",
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                value="2001:db8::2",
            ),
            Record(
                name="name3",
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                value="2001:db8::3",
            ),
            Record(
                name="name4",
                zone=cls.zones[1],
                type=RecordTypeChoices.AAAA,
                value="2001:db8::4",
            ),
        )
        Record.objects.bulk_create(cls.records)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "name": "zone6.example.com",
                "status": "reserved",
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
                "status": "reserved",
                "nameservers": [nameserver.pk for nameserver in nameservers[1:3]],
                **zone_data,
                "soa_mname": nameservers[0].pk,
            },
            {
                "name": "zone8.example.com",
                "status": "reserved",
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

    def test_records_per_zone_with_permission(self):
        zone = self.zones[0]

        self.add_permissions(
            "netbox_dns.view_zone",
            "netbox_dns.view_record",
        )

        url = reverse("plugins-api:netbox_dns-api:zone-records", kwargs={"pk": zone.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_records = [
            record for record in response.json() if not record.get("managed")
        ]
        self.assertEqual(len(response_records), 3)
        for record in self.records[0:3]:
            self.assertTrue(
                record.pk
                in [response_record.get("id") for response_record in response_records]
            )
        self.assertFalse(
            self.records[3].pk
            in [response_record.get("id") for response_record in response_records]
        )

    def test_records_per_zone_without_permission(self):
        zone = self.zones[0]

        self.add_permissions("netbox_dns.view_zone")

        url = reverse("plugins-api:netbox_dns-api:zone-records", kwargs={"pk": zone.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_records = [
            record for record in response.json() if not record.get("managed")
        ]
        self.assertEqual(len(response_records), 0)

    def test_records_per_zone_with_constrained_permission(self):
        zone = self.zones[0]

        self.add_permissions("netbox_dns.view_zone")
        object_permission = ObjectPermission(
            name="View specific records",
            actions=["view"],
            constraints={"name__in": [record.name for record in self.records[0:2]]},
        )
        object_permission.save()
        object_permission.object_types.add(ObjectType.objects.get_for_model(Record))
        object_permission.users.add(self.user)

        url = reverse("plugins-api:netbox_dns-api:zone-records", kwargs={"pk": zone.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_records = [
            record for record in response.json() if not record.get("managed")
        ]
        self.assertEqual(len(response_records), 2)
        for record in self.records[0:2]:
            self.assertTrue(
                record.pk
                in [response_record.get("id") for response_record in response_records]
            )
        for record in self.zones[2:4]:
            self.assertFalse(
                record.pk
                in [response_record.get("id") for response_record in response_records]
            )
