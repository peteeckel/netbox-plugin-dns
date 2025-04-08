from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import (
    APITestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
)
from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    NameServer,
    RegistrationContact,
    Registrar,
)
from netbox_dns.choices import RecordTypeChoices


class ZoneTemplateAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    CustomFieldTargetAPIMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = ZoneTemplate

    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
            NameServer(name="ns4.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

        registrars = (
            Registrar(name="Registrar 1"),
            Registrar(name="Registrar 2"),
        )
        Registrar.objects.bulk_create(registrars)

        contacts = (
            RegistrationContact(contact_id="contact.0001"),
            RegistrationContact(contact_id="contact.0002"),
            RegistrationContact(contact_id="contact.0003"),
            RegistrationContact(contact_id="contact.0004"),
            RegistrationContact(contact_id="contact.0005"),
            RegistrationContact(contact_id="contact.0006"),
        )
        RegistrationContact.objects.bulk_create(contacts)

        record_templates = (
            RecordTemplate(
                name="Record Template 1",
                record_name="@",
                type=RecordTypeChoices.MX,
                value="10 mx1.example.com.",
            ),
            RecordTemplate(
                name="Record Template 2",
                record_name="www",
                type=RecordTypeChoices.CNAME,
                value="@",
            ),
            RecordTemplate(
                name="Record Template 3",
                record_name="@",
                type=RecordTypeChoices.TXT,
                value="v=spf1 +mx -all",
            ),
        )
        RecordTemplate.objects.bulk_create(record_templates)

        zone_templates = (
            ZoneTemplate(
                name="Zone Template 1", registrar=registrars[0], registrant=contacts[0]
            ),
            ZoneTemplate(
                name="Zone Template 2", registrar=registrars[1], tech_c=contacts[1]
            ),
            ZoneTemplate(
                name="Zone Template 3", registrar=registrars[0], admin_c=contacts[2]
            ),
            ZoneTemplate(
                name="Zone Template 4", registrar=registrars[1], billing_c=contacts[3]
            ),
            ZoneTemplate(
                name="Zone Template 5",
                registrar=registrars[0],
                registrant=contacts[4],
                billing_c=contacts[5],
            ),
            ZoneTemplate(
                name="Zone Template 6",
                registrar=registrars[0],
                registrant=contacts[3],
                tech_c=contacts[1],
            ),
        )
        ZoneTemplate.objects.bulk_create(zone_templates)

        cls.create_data = [
            {
                "name": "Zone Template 7",
                "nameservers": [nameserver.pk for nameserver in nameservers[0:1]],
                "soa_mname": nameservers[2].pk,
                "soa_rname": "hostmaster.example.com",
                "record_templates": [
                    record_template.pk for record_template in record_templates[0:3]
                ],
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "tech_c": contacts[0].pk,
                "admin_c": contacts[0].pk,
                "billing_c": contacts[0].pk,
            },
            {
                "name": "Zone Template 8",
                "nameservers": [nameserver.pk for nameserver in nameservers[1:2]],
                "soa_mname": nameservers[0].pk,
                "soa_rname": "hostmaster.example.com",
                "record_templates": [record_templates[1].pk],
                "registrar": registrars[0].pk,
                "registrant": contacts[0].pk,
                "tech_c": contacts[1].pk,
                "admin_c": contacts[2].pk,
                "billing_c": contacts[3].pk,
            },
            {
                "name": "Zone Template 9",
                "nameservers": [nameserver.pk for nameserver in nameservers[2:3]],
                "soa_mname": nameservers[0].pk,
                "soa_rname": "hostmaster2.example.com",
                "record_templates": [record_templates[0].pk, record_templates[2].pk],
                "registrar": registrars[1].pk,
                "registrant": contacts[5].pk,
                "tech_c": contacts[4].pk,
                "admin_c": contacts[4].pk,
                "billing_c": contacts[2].pk,
            },
            {
                "name": "Zone Template 10",
                "record_templates": [
                    record_template.pk for record_template in record_templates[0:3]
                ],
            },
        ]

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.bulk_update_data = {
            "description": "Test Zone Template",
            "nameservers": [nameserver.pk for nameserver in nameservers[1:5]],
            "soa_mname": nameservers[0].pk,
            "soa_rname": "hostmaster3.example.com",
            "record_templates": [record_templates[1].pk, record_templates[2].pk],
            "registrar": registrars[0].pk,
            "tech_c": contacts[0].pk,
            "admin_c": contacts[0].pk,
            "billing_c": contacts[0].pk,
            "tags": [t.pk for t in tags],
        }
