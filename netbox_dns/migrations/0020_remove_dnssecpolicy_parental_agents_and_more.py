# Generated by Django 5.1.8 on 2025-04-22 21:45

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns", "0019_dnssecpolicy_parental_agents"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dnssecpolicy",
            name="parental_agents",
        ),
        migrations.AddField(
            model_name="zone",
            name="parental_agents",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.GenericIPAddressField(),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
    ]
