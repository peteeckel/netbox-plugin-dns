import taggit.managers

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import netbox_dns.fields.address
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.utilities import arpa_to_prefix


def fqdn(record):
    if record.name == "@":
        return f"{record.zone.name}."

    return f"{record.name}.{record.zone.name}."


def address_from_name(record):
    prefix = arpa_to_prefix(fqdn(record))
    if prefix is not None:
        return prefix.ip

    return None


def update_ip_addresses(apps, schema_editor):
    Record = apps.get_model("netbox_dns", "Record")

    for record in Record.objects.filter(type=RecordTypeChoices.PTR):
        record.ip_address = address_from_name(record)
        record.save()

    for record in Record.objects.filter(
        type__in=(RecordTypeChoices.A, RecordTypeChoices.AAAA)
    ):
        record.ip_address = record.value
        record.save()


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0084_staging"),
        ("netbox_dns", "0020_netbox_3_4"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="ip_address",
            field=netbox_dns.fields.address.AddressField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="record",
            name="tags",
            field=taggit.managers.TaggableManager(
                through="extras.TaggedItem", to="extras.Tag"
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_expire",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_minimum",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_mname",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones_soa",
                to="netbox_dns.nameserver",
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_refresh",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_retry",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_rname",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="zone",
            name="soa_ttl",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.RunPython(update_ip_addresses),
    ]
