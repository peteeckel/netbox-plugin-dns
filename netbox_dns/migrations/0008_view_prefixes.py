from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ipam", "0067_ipaddress_index_host"),
        ("netbox_dns", "0007_alter_ordering_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="view",
            name="prefixes",
            field=models.ManyToManyField(
                blank=True, related_name="netbox_dns_views", to="ipam.prefix"
            ),
        ),
    ]
