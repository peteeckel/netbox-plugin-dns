from django.db import migrations


def update_ns_ttl(apps, schema_editor):
    Zone = apps.get_model("netbox_dns", "Zone")

    for zone in Zone.objects.all():
        for nameserver in zone.nameservers.all():
            nameserver.ttl = None


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns", "0017_alter_record_ttl"),
    ]

    operations = [
        migrations.RunPython(update_ns_ttl),
    ]
