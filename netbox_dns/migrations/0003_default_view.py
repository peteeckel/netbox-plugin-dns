from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0002_contact_description_registrar_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="view",
            name="default_view",
            field=models.BooleanField(default=False),
        ),
    ]
