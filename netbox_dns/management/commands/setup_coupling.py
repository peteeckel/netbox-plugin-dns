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
        parser.add_argument("--verbose", action="store_true", help="Verbose output")

    def handle(self, *model_names, **options):
        ipaddress_object_type = ContentType.objects.get_for_model(IPAddress)

        if options["remove"]:
            for cf in (
                "ipaddress_dns_record_name",
                "ipaddress_dns_record_ttl",
                "ipaddress_dns_record_disable_ptr",
                "ipaddress_dns_zone_id",
            ):
                try:
                    CustomField.objects.get(
                        name=cf, content_types=ipaddress_object_type
                    ).delete()
                    if options.get("verbose"):
                        self.stdout.write(f"Custom field '{cf}' removed")
                except:
                    pass

        else:
            if not CustomField.objects.filter(
                name="ipaddress_dns_record_name",
                type=CustomFieldTypeChoices.TYPE_TEXT,
                content_types=ipaddress_object_type,
            ).exists():
                cf_name = CustomField.objects.create(
                    name="ipaddress_dns_record_name",
                    label="Name",
                    type=CustomFieldTypeChoices.TYPE_TEXT,
                    required=False,
                    group_name="DNS",
                )
                cf_name.content_types.set([ipaddress_object_type])
                if options.get("verbose"):
                    self.stdout.write(
                        "Created custom field 'ipaddress_dns_record_name'"
                    )

            if not CustomField.objects.filter(
                name="ipaddress_dns_record_ttl",
                type=CustomFieldTypeChoices.TYPE_INTEGER,
                content_types=ipaddress_object_type,
            ).exists():
                cf_ttl = CustomField.objects.create(
                    name="ipaddress_dns_record_ttl",
                    label="TTL",
                    type=CustomFieldTypeChoices.TYPE_INTEGER,
                    validation_minimum=0,
                    validation_maximum=2147483647,
                    required=False,
                    group_name="DNS",
                )
                cf_ttl.content_types.set([ipaddress_object_type])
                if options.get("verbose"):
                    self.stdout.write("Created custom field 'ipaddress_dns_record_ttl'")

            if not CustomField.objects.filter(
                name="ipaddress_dns_record_disable_ptr",
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                content_types=ipaddress_object_type,
            ).exists():
                cf_disable_ptr = CustomField.objects.create(
                    name="ipaddress_dns_record_disable_ptr",
                    label="Disable PTR",
                    type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                    required=False,
                    default=False,
                    group_name="DNS",
                )
                cf_disable_ptr.content_types.set([ipaddress_object_type])
                if options.get("verbose"):
                    self.stdout.write(
                        "Created custom field 'ipaddress_dns_record_disable_ptr'"
                    )

            if not CustomField.objects.filter(
                name="ipaddress_dns_zone_id",
                type=CustomFieldTypeChoices.TYPE_OBJECT,
                content_types=ipaddress_object_type,
            ).exists():
                cf_zone = CustomField.objects.create(
                    name="ipaddress_dns_zone_id",
                    label="Zone",
                    type=CustomFieldTypeChoices.TYPE_OBJECT,
                    object_type=ContentType.objects.get_for_model(Zone),
                    required=False,
                    group_name="DNS",
                )
                cf_zone.content_types.set([ipaddress_object_type])
                if options.get("verbose"):
                    self.stdout.write("Created custom field 'ipaddress_dns_zone_id'")
