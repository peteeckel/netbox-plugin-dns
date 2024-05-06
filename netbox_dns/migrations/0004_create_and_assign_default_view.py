from django.db import migrations


def create_and_assign_default_view(apps, schema_editor):
    View = apps.get_model("netbox_dns", "View")
    Zone = apps.get_model("netbox_dns", "Zone")

    default_view = View.objects.create(
        name="_default_",
        description="Default View",
        default_view=True,
    )

    for zone in Zone.objects.filter(view=None):
        zone.view = default_view
        zone.save()


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0003_default_view"),
    ]

    operations = [
        migrations.RunPython(create_and_assign_default_view),
    ]
