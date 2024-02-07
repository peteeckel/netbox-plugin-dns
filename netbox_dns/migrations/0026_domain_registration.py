from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_dns", "0025_ipam_coupling_cf"),
        ("extras", "0092_delete_jobresult"),
    ]

    operations = [
        migrations.CreateModel(
            name="Registrar",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("iana_id", models.IntegerField(blank=True)),
                ("referral_url", models.URLField(blank=True, max_length=255)),
                ("whois_server", models.CharField(blank=True, max_length=255)),
                ("address", models.CharField(blank=True, max_length=200)),
                ("abuse_email", models.EmailField(blank=True, max_length=254)),
                ("abuse_phone", models.CharField(blank=True, max_length=50)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("name", "iana_id"),
            },
        ),
        migrations.CreateModel(
            name="Contact",
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
                ("name", models.CharField(blank=True, max_length=100)),
                ("contact_id", models.CharField(max_length=50, unique=True)),
                ("organization", models.CharField(blank=True, max_length=200)),
                ("street", models.CharField(blank=True, max_length=50)),
                ("city", models.CharField(blank=True, max_length=50)),
                ("state_province", models.CharField(blank=True, max_length=255)),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("country", models.CharField(blank=True, max_length=2)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("phone_ext", models.CharField(blank=True, max_length=50)),
                ("fax", models.CharField(blank=True, max_length=50)),
                ("fax_ext", models.CharField(blank=True, max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("name", "contact_id"),
            },
        ),
        migrations.AddField(
            model_name="zone",
            name="admin_c",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="admin_c_zones",
                to="netbox_dns.contact",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="billing_c",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="billing_c_zones",
                to="netbox_dns.contact",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="registrant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="netbox_dns.contact",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="registrar",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="netbox_dns.registrar",
            ),
        ),
        migrations.AddField(
            model_name="zone",
            name="registry_domain_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="zone",
            name="tech_c",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tech_c_zones",
                to="netbox_dns.contact",
            ),
        ),
    ]
