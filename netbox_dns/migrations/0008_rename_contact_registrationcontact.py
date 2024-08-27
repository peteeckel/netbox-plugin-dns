from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_dns", "0007_alter_ordering_options"),
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
    ]
