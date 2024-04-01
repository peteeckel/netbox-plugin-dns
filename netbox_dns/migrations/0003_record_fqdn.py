from dns import name as dns_name

from django.db import migrations, models


def update_record_fqdn(apps, schema_editor):
    Record = apps.get_model("netbox_dns", "Record")

    for record in Record.objects.filter(fqdn__isnull=True):
        zone = dns_name.from_text(record.zone.name, origin=dns_name.root)
        fqdn = dns_name.from_text(record.name, origin=zone)

        record.fqdn = fqdn.to_text()

        record.save()


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0028_rfc2317_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="fqdn",
            field=models.CharField(default=None, max_length=255, null=True, blank=True),
        ),
        migrations.RunPython(update_record_fqdn),
    ]
