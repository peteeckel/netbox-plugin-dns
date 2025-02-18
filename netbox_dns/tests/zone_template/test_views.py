from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    NameServer,
    Registrar,
    RegistrationContact,
)
from netbox_dns.choices import RecordTypeChoices


class ZoneTemplateViewTestCase(
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
    model = ZoneTemplate

    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

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
            ZoneTemplate(name="Zone Template 1"),
            ZoneTemplate(name="Zone Template 2"),
            ZoneTemplate(name="Zone Template 3"),
        )
        ZoneTemplate.objects.bulk_create(zone_templates)
        for zone_template in zone_templates:
            zone_template.nameservers.set(nameservers[0:1])

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Zone Template 4",
            "nameservers": [nameserver.pk for nameserver in nameservers[1:2]],
            "soa_mname": nameservers[0].pk,
            "soa_rname": "hostmaster.example.com",
            "record_templates": [
                record_template.pk for record_template in record_templates[0:2]
            ],
            "registrar": registrars[0].pk,
            "registrant": contacts[0].pk,
            "admin_c": contacts[1].pk,
            "tech_c": contacts[2].pk,
            "billing_c": contacts[3].pk,
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "registrar": registrars[1].pk,
            "registrant": contacts[3].pk,
            "admin_c": contacts[2].pk,
            "tech_c": contacts[1].pk,
            "billing_c": contacts[0].pk,
            "nameservers": [nameserver.pk for nameserver in nameservers[1:3]],
            "soa_rname": "hostmaster.example.com",
            "record_templates": [
                record_template.pk for record_template in record_templates[1:3]
            ],
            "tag": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,nameservers,soa_rname,soa_mname,record_templates,registrar,registrant,admin_c,tech_c,billing_c",
            f"Zone Template 5,\"{','.join(nameserver.name for nameserver in nameservers[0:1])}\",hostmaster.example.com,{nameservers[0].name},\"{','.join(record_template.name for record_template in record_templates[0:1])}\",{registrars[0].name},{contacts[0].contact_id},{contacts[1].contact_id},{contacts[2].contact_id},{contacts[3].contact_id}",
            f"Zone Template 6,\"{','.join(nameserver.name for nameserver in nameservers[1:2])}\",,{nameservers[1].name},,{registrars[1].name},{contacts[2].contact_id},{contacts[3].contact_id},{contacts[0].contact_id},{contacts[1].contact_id}",
            f"Zone Template 7,\"{','.join(nameserver.name for nameserver in nameservers[0:1])}\",hostmaster.example.com,,,{registrars[0].name},{contacts[3].contact_id},{contacts[2].contact_id},{contacts[1].contact_id},{contacts[3].contact_id}",
            f"Zone Template 8,,,,,{registrars[1].name},{contacts[0].contact_id},,{contacts[2].contact_id},",
        )

        cls.csv_update_data = (
            "id,soa_mname,record_templates,registrar,registrant,billing_c,tech_c,admin_c",
            f'{zone_templates[0].pk},{nameservers[0].name},"{record_templates[0].name},{record_templates[1].name}",{registrars[0].name},{contacts[0].contact_id},{contacts[1].contact_id},{contacts[2].contact_id},{contacts[3].contact_id}',
        )
