# Generated by Django 5.1.6 on 2025-03-10 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns", "0016_dnssec_policy_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="dnssec_policy",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones",
                to="netbox_dns.dnssecpolicy",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="inline_signing",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="zonetemplate",
            name="dnssec_policy",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="zone_templates",
                to="netbox_dns.dnssecpolicy",
            ),
        ),
    ]
