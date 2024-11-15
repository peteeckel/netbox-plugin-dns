import re
import textwrap

from django.test import TestCase

from core.models import ObjectType
from extras.models import CustomField
from extras.choices import CustomFieldTypeChoices

from netbox_dns.models import Zone, Record, NameServer
from netbox_dns.choices import RecordTypeChoices


def split_text_value(value):
    raw_value = "".join(re.findall(r'"([^"]+)"', value))
    if not raw_value:
        raw_value = value

    return " ".join(
        f'"{part}"' for part in textwrap.wrap(raw_value, 255, drop_whitespace=False)
    )


class RecordCustomFieldTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        nameserver = NameServer.objects.create(name="ns1.example.com")

        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        cls.records = [
            Record(
                zone=zone,
                name="test1",
                type=RecordTypeChoices.A,
                value="10.0.1.42",
            ),
            Record(
                zone=zone,
                name="test2",
                type=RecordTypeChoices.AAAA,
                value="fe80:dead:beef::1:42",
            ),
            Record(
                zone=zone,
                name="test3",
                type=RecordTypeChoices.TXT,
                value="this is a test record",
            ),
        ]
        for record in cls.records:
            record.save()

        cf = CustomField.objects.create(
            name="test_cf",
            label="Test CF",
            type=CustomFieldTypeChoices.TYPE_INTEGER,
            required=False,
        )
        cf.object_types.set([ObjectType.objects.get_for_model(Record)])

    def test_custom_field_set(self):
        for record in self.records:
            record.custom_field_data["test_cf"] = 42
            record.save()

            record.refresh_from_db()

            self.assertEqual(record.custom_field_data.get("test_cf"), 42)

    def test_custom_field_modify(self):
        for record in self.records:
            record.custom_field_data["test_cf"] = 42
            record.save()

            record.custom_field_data["test_cf"] = 23
            record.save()

            record.refresh_from_db()

            self.assertEqual(record.custom_field_data.get("test_cf"), 23)
