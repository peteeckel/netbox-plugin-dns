# Generated by Django 5.1.6 on 2025-03-02 18:13

import django.contrib.postgres.fields
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0122_charfield_null_choices"),
        ("netbox_dns", "0014_alter_unique_constraints_lowercase"),
        ("tenancy", "0017_natural_ordering"),
    ]

    operations = [
        migrations.CreateModel(
            name="DNSSECKey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("type", models.CharField(max_length=3)),
                ("lifetime", models.PositiveIntegerField(blank=True, null=True)),
                ("algorithm", models.CharField()),
                ("key_size", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="netbox_dns_dnssec_keys",
                        to="tenancy.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "DNSSEC Key",
                "verbose_name_plural": "DNSSEC Keys",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="DNSSECPolicy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("inline_signing", models.BooleanField(default=True)),
                ("dnskey_ttl", models.PositiveIntegerField(blank=True, null=True)),
                ("purge_keys", models.PositiveIntegerField(blank=True, null=True)),
                ("publish_safety", models.PositiveIntegerField(blank=True, null=True)),
                ("retire_safety", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "signatures_jitter",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "signatures_refresh",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "signatures_validity",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "signatures_validity_dnskey",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("max_zone_ttl", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "zone_propagation_delay",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("create_cdnskey", models.BooleanField(default=True)),
                (
                    "cds_digest_types",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(), default=list, size=None
                    ),
                ),
                ("parent_ds_ttl", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "parent_propagation_delay",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("use_nsec3", models.BooleanField(default=True)),
                (
                    "nsec3_iterations",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("nsec3_opt_out", models.BooleanField(blank=True, null=True)),
                ("nsec3_salt_size", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "keys",
                    models.ManyToManyField(
                        blank=True, related_name="policies", to="netbox_dns.dnsseckey"
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="netbox_dns_dnssec_policy",
                        to="tenancy.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "DNSSEC Key",
                "verbose_name_plural": "DNSSEC Keys",
                "ordering": ("name",),
            },
        ),
    ]
