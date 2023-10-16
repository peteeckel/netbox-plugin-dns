from django.core.management.base import BaseCommand, CommandError

from django.contrib.contenttypes.models import ContentType
from extras.models import CustomField
from extras.choices import CustomFieldTypeChoices
from ipam.models import IPAddress
from netbox_dns.models import Record, Zone


class Command(BaseCommand):
    help = "Setup IPAddress custom fields needed for IPAM-DNS coupling"

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove", action="store_true", help="Remove custom fields"
        )

    def handle(self, *model_names, **options):
        ipaddress_object_type = ContentType.objects.get_for_model(IPAddress)
        zone_object_type = ContentType.objects.get_for_model(Zone)
        record_object_type = ContentType.objects.get_for_model(Record)
        customfields = ("ipaddress_dns_record_name", "ipaddress_dns_zone_id")

        if options["remove"]:
            for cf in customfields:
                try:
                    CustomField.objects.get(
                        name=cf, content_types=ipaddress_object_type
                    ).delete()
                except:
                    self.stderr.write(f"Custom field '{cf}' does not exist!")
                else:
                    self.stdout.write(f"Custom field '{cf}' removed")

        else:
            msg = ""
            for cf in customfields:
                try:
                    CustomField.objects.get(
                        name=cf, content_types=ipaddress_object_type
                    )
                except:
                    pass
                else:
                    msg += f"custom fields '{cf}' already exists, "
            if msg != "":
                raise CommandError(
                    "\n".join(
                        (
                            "Can't setup IPAM-DNS coupling:",
                            msg,
                            "Remove them with NetBox command:",
                            "python manage.py setup_coupling --remove",
                        )
                    )
                )

            cf_name = CustomField.objects.create(
                name="ipaddress_dns_record_name",
                label="Name",
                type=CustomFieldTypeChoices.TYPE_TEXT,
                required=False,
                group_name="DNS",
            )
            cf_name.content_types.set([ipaddress_object_type])
            cf_zone = CustomField.objects.create(
                name="ipaddress_dns_zone_id",
                label="Zone",
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                object_type=zone_object_type,
                required=False,
                group_name="DNS",
            )
            cf_zone.content_types.set([ipaddress_object_type])
            self.stdout.write(f"Custom fields for IPAM-DNS coupling added")
