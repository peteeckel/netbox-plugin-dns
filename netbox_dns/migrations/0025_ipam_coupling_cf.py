from django.db import migrations
from django.contrib.contenttypes.models import ContentType

from extras.models import CustomField

from extras.choices import CustomFieldTypeChoices, CustomFieldVisibilityChoices
from ipam.models import IPAddress, Prefix
from netbox_dns.models import Record, RecordTypeChoices, Zone, NameServer


def add_ipam_coupling_cf(apps, schema_editor):
    # CustomField = apps.get_model("extras", "CustomField")
    # IPAddress = apps.get_model("ipam", "IPAddress")
    # Zone = apps.get_model("netbox_dns", "Zone")
    # Record = apps.get_model("netbox_dns", "Record")

    ipaddress_object_type = ContentType.objects.get_for_model(IPAddress)
    zone_object_type = ContentType.objects.get_for_model(Zone)
    record_object_type = ContentType.objects.get_for_model(Record)
    cf_name = CustomField.objects.create(
        name="name", type=CustomFieldTypeChoices.TYPE_TEXT, required=False
    )
    cf_name.content_types.set([ipaddress_object_type])
    cf_zone = CustomField.objects.create(
        name="zone",
        type=CustomFieldTypeChoices.TYPE_OBJECT,
        object_type=zone_object_type,
        required=False,
    )
    cf_zone.content_types.set([ipaddress_object_type])
    cf_dns_record = CustomField.objects.create(
        name="dns_record",
        type=CustomFieldTypeChoices.TYPE_OBJECT,
        object_type=record_object_type,
        required=False,
        ui_visibility=CustomFieldVisibilityChoices.VISIBILITY_READ_ONLY,
    )
    cf_dns_record.content_types.set([ipaddress_object_type])


def delete_ipam_coupling_cf(apps, schema_editor):
    ipaddress_object_type = ContentType.objects.get_for_model(IPAddress)
    CustomField.objects.get(name="name", content_types=ipaddress_object_type).delete()
    CustomField.objects.get(name="zone", content_types=ipaddress_object_type).delete()
    CustomField.objects.get(
        name="dns_record", content_types=ipaddress_object_type
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0024_tenancy"),
    ]

    operations = [
        migrations.RunPython(add_ipam_coupling_cf, reverse_code=delete_ipam_coupling_cf)
    ]
