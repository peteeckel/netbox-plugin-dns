from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ipam", "0066_iprange_mark_utilized"),
        ("netbox_dns", "0024_tenancy"),
    ]
    operations = [
        migrations.AddField(
            model_name="record",
            name="ipam_ip_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="netbox_dns_records",
                to="ipam.ipaddress",
            ),
        ),
    ]
