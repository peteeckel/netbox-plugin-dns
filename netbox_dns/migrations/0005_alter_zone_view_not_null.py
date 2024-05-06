import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0004_create_and_assign_default_view"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zone",
            name="view",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="netbox_dns.view"
            ),
        ),
    ]
