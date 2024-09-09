from django.db import migrations, connection


def remove_object_changes(apps, schema_editor):
    if "objectchange" in apps.all_models.get("core"):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM core_objectchange WHERE changed_object_type_id in (SELECT id FROM django_content_type WHERE app_label='netbox_dns' AND model='contact')"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns", "0008_view_prefixes"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Contact",
            new_name="RegistrationContact",
        ),
        migrations.RunSQL(
            "ALTER TABLE netbox_dns_contact_id_seq RENAME TO netbox_dns_registrationcontact_id_seq"
        ),
        migrations.RunSQL(
            "ALTER INDEX netbox_dns_contact_pkey RENAME TO netbox_dns_registrationcontact_pkey"
        ),
        migrations.RunSQL(
            "ALTER INDEX netbox_dns_contact_contact_id_50e9d89d_like RENAME TO netbox_dns_registrationcontact_contact_id_6ff98464_like"
        ),
        migrations.RunSQL(
            "ALTER INDEX netbox_dns_contact_contact_id_key RENAME TO netbox_dns_contact_registrationcontact_id_key"
        ),
        migrations.RunPython(remove_object_changes),
    ]
