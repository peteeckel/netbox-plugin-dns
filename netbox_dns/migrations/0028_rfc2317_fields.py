from django.db import migrations, models
import django.db.models.deletion
import netbox_dns.fields.rfc2317


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0027_alter_registrar_iana_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="rfc2317_prefix",
            field=netbox_dns.fields.rfc2317.RFC2317NetworkField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="zone",
            name="rfc2317_parent_managed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="zone",
            name="rfc2317_parent_zone",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rfc2317_child_zones",
                to="netbox_dns.zone",
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="rfc2317_cname_record",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rfc2317_ptr_records",
                to="netbox_dns.record",
            ),
        ),
    ]
