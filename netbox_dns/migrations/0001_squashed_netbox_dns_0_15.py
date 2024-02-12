import taggit.managers

import django.core.serializers.json
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import netbox_dns.fields.network


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0073_journalentry_tags_custom_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="NameServer",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="View",
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
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Zone",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(blank=True, default="active", max_length=50),
                ),
                (
                    "nameservers",
                    models.ManyToManyField(
                        blank=True, related_name="zones", to="netbox_dns.nameserver"
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "view",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="netbox_dns.view",
                    ),
                ),
                (
                    "default_ttl",
                    models.PositiveIntegerField(
                        blank=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "soa_expire",
                    models.PositiveIntegerField(
                        default=2592000,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "soa_minimum",
                    models.PositiveIntegerField(
                        default=3600,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "soa_mname",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="zones_soa",
                        to="netbox_dns.nameserver",
                    ),
                ),
                (
                    "soa_refresh",
                    models.PositiveIntegerField(
                        default=172800,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "soa_retry",
                    models.PositiveIntegerField(
                        default=7200,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "soa_rname",
                    models.CharField(default="hostmaster.example.com", max_length=255),
                ),
                (
                    "soa_serial",
                    models.BigIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(4294967295),
                        ],
                    ),
                ),
                (
                    "soa_ttl",
                    models.PositiveIntegerField(
                        default=86400,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                ("soa_serial_auto", models.BooleanField(default=True)),
                (
                    "arpa_network",
                    netbox_dns.fields.network.NetworkField(blank=True, null=True),
                ),
            ],
            options={
                "ordering": ("view", "name"),
                "unique_together": {("view", "name")},
            },
        ),
        migrations.CreateModel(
            name="Record",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                    ),
                ),
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("type", models.CharField(max_length=10)),
                ("name", models.CharField(max_length=255)),
                ("value", models.CharField(max_length=1000)),
                ("ttl", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="extras.TaggedItem",
                        to="extras.Tag",
                        verbose_name="Tags",
                    ),
                ),
                (
                    "zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="netbox_dns.zone",
                    ),
                ),
                ("status", models.CharField(default="active", max_length=50)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("managed", models.BooleanField(default=False)),
                ("disable_ptr", models.BooleanField(default=False)),
                (
                    "ptr_record",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="address_record",
                        to="netbox_dns.record",
                    ),
                ),
            ],
            options={
                "ordering": ("zone", "name", "type", "value", "status"),
            },
        ),
    ]
