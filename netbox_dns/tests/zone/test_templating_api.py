from django.urls import reverse
from rest_framework import status

from utilities.testing import APITestCase, create_tags
from tenancy.models import Tenant

from netbox_dns.models import (
    NameServer,
    Registrar,
    RegistrationContact,
    RecordTemplate,
    ZoneTemplate,
    Zone,
    Record,
    DNSSECPolicy,
)
from netbox_dns.choices import RecordTypeChoices


class ZoneTemplatingAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tags = create_tags("Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot")

        cls.tenants = (
            Tenant(name="Tenant 1", slug="tenant-1"),
            Tenant(name="Tenant 2", slug="tenant-2"),
        )
        Tenant.objects.bulk_create(cls.tenants)

        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
            NameServer(name="ns4.example.com"),
            NameServer(name="ns5.example.com"),
            NameServer(name="ns6.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        cls.registrars = (
            Registrar(name="Registrar 1"),
            Registrar(name="Registrar 2"),
        )
        Registrar.objects.bulk_create(cls.registrars)

        cls.contacts = (
            RegistrationContact(contact_id="contact-1"),
            RegistrationContact(contact_id="contact-2"),
            RegistrationContact(contact_id="contact-3"),
            RegistrationContact(contact_id="contact-4"),
            RegistrationContact(contact_id="contact-5"),
        )
        RegistrationContact.objects.bulk_create(cls.contacts)

        cls.dnssec_policies = (
            DNSSECPolicy(name="Test Policy 1"),
            DNSSECPolicy(name="Test Policy 2"),
            DNSSECPolicy(name="Test Policy 3"),
        )
        DNSSECPolicy.objects.bulk_create(cls.dnssec_policies)

        cls.record_templates = (
            RecordTemplate(
                name="Primary MX",
                record_name="@",
                type=RecordTypeChoices.MX,
                value="10 mx1.example.com.",
            ),
            RecordTemplate(
                name="Secondary MX",
                record_name="@",
                type=RecordTypeChoices.MX,
                value="20 mx2.example.com.",
            ),
            RecordTemplate(
                name="Strict SPF",
                record_name="@",
                type=RecordTypeChoices.TXT,
                value="v=spf1 +mx -all",
            ),
        )
        RecordTemplate.objects.bulk_create(cls.record_templates)

        cls.zone_template = ZoneTemplate.objects.create(
            name="Test Zone Template",
            soa_mname=cls.nameservers[0],
            soa_rname="hostmaster.example.com",
            registrar=cls.registrars[0],
            registrant=cls.contacts[0],
            admin_c=cls.contacts[1],
            tech_c=cls.contacts[2],
            billing_c=cls.contacts[3],
            tenant=cls.tenants[0],
            dnssec_policy=cls.dnssec_policies[0],
            parental_agents=["2001:db8:42::42", "2001:db8:23::23"],
        )
        cls.zone_template.tags.set(cls.tags[0:3])
        cls.zone_template.nameservers.set(cls.nameservers[0:3])
        cls.zone_template.record_templates.set(cls.record_templates)

    def test_create_zone(self):
        self.add_permissions("netbox_dns.add_zone")
        self.add_permissions("extras.view_tag")

        url = reverse("plugins-api:netbox_dns-api:zone-list")

        data = {
            "name": "test.example.com",
            "template": {
                "name": self.zone_template.name,
            },
            **Zone.get_defaults(),
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        zones = Zone.objects.filter(name="test.example.com")
        self.assertEqual(zones.count(), 1)
        zone = zones.first()

        self.assertEqual(zone.soa_mname, self.nameservers[0])
        self.assertEqual(zone.soa_rname, "hostmaster.example.com")
        self.assertEqual(zone.registrar, self.registrars[0])
        self.assertEqual(zone.registrant, self.contacts[0])
        self.assertEqual(zone.admin_c, self.contacts[1])
        self.assertEqual(zone.tech_c, self.contacts[2])
        self.assertEqual(zone.billing_c, self.contacts[3])
        self.assertEqual(zone.tenant, self.tenants[0])
        self.assertEqual(zone.dnssec_policy, self.dnssec_policies[0])
        self.assertEqual(zone.parental_agents, ["2001:db8:42::42", "2001:db8:23::23"])

        self.assertEqual(set(zone.nameservers.all()), set(self.nameservers[0:3]))
        self.assertEqual(set(zone.tags.all()), set(self.tags[0:3]))

        for record_template in self.record_templates:
            self.assertTrue(
                Record.objects.filter(
                    zone=zone,
                    name=record_template.record_name,
                    type=record_template.type,
                    value=record_template.value,
                ).exists()
            )

    def test_create_zone_override_fields(self):
        self.add_permissions("netbox_dns.add_zone")
        self.add_permissions("extras.view_tag")

        url = reverse("plugins-api:netbox_dns-api:zone-list")

        data = {
            "name": "test.example.com",
            "soa_mname": {
                "name": self.nameservers[4].name,
            },
            "soa_rname": "hostmaster2.example.com",
            "template": {
                "name": self.zone_template.name,
            },
            "registrar": {
                "name": "Registrar 2",
            },
            "registrant": {
                "contact_id": "contact-5",
            },
            "admin_c": {
                "contact_id": "contact-5",
            },
            "tech_c": {
                "contact_id": "contact-5",
            },
            "billing_c": {
                "contact_id": "contact-5",
            },
            "tenant": {
                "name": "Tenant 2",
            },
            "tags": [
                {
                    "slug": "delta",
                },
                {
                    "slug": "echo",
                },
                {
                    "slug": "foxtrot",
                },
            ],
            "nameservers": [
                {
                    "name": "ns4.example.com",
                },
                {
                    "name": "ns5.example.com",
                },
                {
                    "name": "ns6.example.com",
                },
            ],
            "dnssec_policy": {
                "name": self.dnssec_policies[1].name,
            },
            "parental_agents": ["2001:db8:42::23", "2001:db8:23::42"],
            **Zone.get_defaults(),
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        zones = Zone.objects.filter(name="test.example.com")
        self.assertEqual(zones.count(), 1)
        zone = zones.first()

        self.assertEqual(zone.soa_mname, self.nameservers[4])
        self.assertEqual(zone.soa_rname, "hostmaster2.example.com")
        self.assertEqual(zone.registrar, self.registrars[1])
        self.assertEqual(zone.registrant, self.contacts[4])
        self.assertEqual(zone.admin_c, self.contacts[4])
        self.assertEqual(zone.tech_c, self.contacts[4])
        self.assertEqual(zone.billing_c, self.contacts[4])
        self.assertEqual(zone.tenant, self.tenants[1])
        self.assertEqual(zone.dnssec_policy, self.dnssec_policies[1])
        self.assertEqual(zone.parental_agents, ["2001:db8:42::23", "2001:db8:23::42"])

        self.assertEqual(set(zone.nameservers.all()), set(self.nameservers[3:6]))
        self.assertEqual(set(zone.tags.all()), set(self.tags[3:6]))

        for record_template in self.record_templates:
            self.assertTrue(
                Record.objects.filter(
                    zone=zone,
                    name=record_template.record_name,
                    type=record_template.type,
                    value=record_template.value,
                ).exists()
            )

    def test_update_zone(self):
        self.add_permissions("netbox_dns.change_zone")

        zone = Zone.objects.create(
            name="test.example.com",
            soa_mname=self.nameservers[5],
            soa_rname="hostmaster3.example.com",
        )

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})

        data = {
            "template": {
                "name": self.zone_template.name,
            },
        }

        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        zone.refresh_from_db()

        self.assertEqual(zone.registrar, self.registrars[0])
        self.assertEqual(zone.registrant, self.contacts[0])
        self.assertEqual(zone.admin_c, self.contacts[1])
        self.assertEqual(zone.tech_c, self.contacts[2])
        self.assertEqual(zone.billing_c, self.contacts[3])
        self.assertEqual(zone.tenant, self.tenants[0])

        self.assertEqual(set(zone.nameservers.all()), set(self.nameservers[0:3]))
        self.assertEqual(set(zone.tags.all()), set(self.tags[0:3]))

        for record_template in self.record_templates:
            self.assertTrue(
                Record.objects.filter(
                    zone=zone,
                    name=record_template.record_name,
                    type=record_template.type,
                    value=record_template.value,
                ).exists()
            )

    def test_create_zone_missing_soa_mname(self):
        self.add_permissions("netbox_dns.add_zone")
        self.add_permissions("extras.view_tag")

        url = reverse("plugins-api:netbox_dns-api:zone-list")

        self.zone_template.soa_mname = None
        self.zone_template.save()

        data = {
            "name": "test.example.com",
            "template": {
                "name": self.zone_template.name,
            },
            **Zone.get_defaults(),
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "soa_mname not set and no template or default value defined"
            in response.json().get("soa_mname")
        )

    def test_create_zone_missing_soa_rname(self):
        self.add_permissions("netbox_dns.add_zone")
        self.add_permissions("extras.view_tag")

        url = reverse("plugins-api:netbox_dns-api:zone-list")

        self.zone_template.soa_rname = ""
        self.zone_template.save()

        data = {
            "name": "test.example.com",
            "template": {
                "name": self.zone_template.name,
            },
            **Zone.get_defaults(),
        }

        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "soa_rname not set and no template or default value defined"
            in response.json().get("soa_rname")
        )
