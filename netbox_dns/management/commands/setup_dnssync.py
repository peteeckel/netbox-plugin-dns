from django.core.management.base import BaseCommand

from core.models import ObjectType
from extras.models import CustomField
from extras.choices import CustomFieldTypeChoices
from ipam.models import IPAddress


class Command(BaseCommand):
    help = "Setup IPAddress custom fields for IPAM DNSsync"

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove", action="store_true", default=False, help="Remove custom fields"
        )

    def handle(self, *model_names, **options):
        ipaddress_object_type = ObjectType.objects.get_for_model(IPAddress)

        if options.get("remove"):
            if options.get("verbosity"):
                self.stdout.write("Trying to remove IPAM DNSsync custom fields")
            for cf in (
                "ipaddress_dns_disabled",
                "ipaddress_dns_record_ttl",
                "ipaddress_dns_record_disable_ptr",
            ):
                try:
                    CustomField.objects.get(
                        name=cf, object_types=ipaddress_object_type
                    ).delete()
                    if options.get("verbosity"):
                        self.stdout.write(f"Removed custom field '{cf}'")
                except CustomField.DoesNotExist:
                    pass
            return

        # +
        # Remove pre-existing IPAM Coupling custom fields
        # -
        if options.get("verbosity") >= 2:
            self.stdout.write("Trying to remove obsolete IPAM Coupling custom fields")
        for cf in (
            "ipaddress_dns_record_name",
            "ipaddress_dns_zone_id",
        ):
            try:
                CustomField.objects.get(
                    name=cf, object_types=ipaddress_object_type
                ).delete()
                if options.get("verbosity"):
                    self.stdout.write(f"Removed custom field '{cf}'")
            except CustomField.DoesNotExist:
                pass

        if options.get("verbosity") >= 2:
            self.stdout.write("Creating IPAM DNSsync custom fields")

        if not CustomField.objects.filter(
            name="ipaddress_dns_disabled",
            type=CustomFieldTypeChoices.TYPE_BOOLEAN,
            object_types=ipaddress_object_type,
        ).exists():
            cf_dnssync_disabled = CustomField.objects.create(
                name="ipaddress_dns_disabled",
                label="Disable DNSsync",
                description="Disable DNS address and pointer record generation for this address",
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                required=False,
                default=False,
                group_name="DNSsync",
                is_cloneable=True,
                weight=100,
            )
            cf_dnssync_disabled.object_types.set([ipaddress_object_type])
            if options.get("verbosity"):
                self.stdout.write("Created custom field 'ipaddress_dns_disabled'")

        try:
            cf_ttl = CustomField.objects.get(
                name="ipaddress_dns_record_ttl",
                type=CustomFieldTypeChoices.TYPE_INTEGER,
                object_types=ipaddress_object_type,
            )
            if cf_ttl.group_name != "DNSsync":
                cf_ttl.group_name = "DNSsync"
                cf_ttl.description = ("TTL for DNS records created for this address",)
                cf_ttl.save()
                if options.get("verbosity"):
                    self.stdout.write("Updated custom field 'ipaddress_dns_record_ttl'")
        except CustomField.DoesNotExist:
            cf_ttl = CustomField.objects.create(
                name="ipaddress_dns_record_ttl",
                description="TTL for DNS records created for this address",
                label="TTL",
                type=CustomFieldTypeChoices.TYPE_INTEGER,
                validation_minimum=0,
                validation_maximum=2147483647,
                required=False,
                group_name="DNSsync",
                is_cloneable=True,
                weight=200,
            )
            cf_ttl.object_types.set([ipaddress_object_type])
            if options.get("verbosity"):
                self.stdout.write("Created custom field 'ipaddress_dns_record_ttl'")

        try:
            cf_disable_ptr = CustomField.objects.get(
                name="ipaddress_dns_record_disable_ptr",
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                object_types=ipaddress_object_type,
            )
            if cf_disable_ptr.group_name != "DNSsync":
                cf_disable_ptr.group_name = "DNSsync"
                cf_disable_ptr.description = (
                    "Disable DNS PTR record generation for this address",
                )
                cf_disable_ptr.save()
                if options.get("verbosity"):
                    self.stdout.write(
                        "Updated custom field 'ipaddress_dns_record_disable_ptr'"
                    )
        except CustomField.DoesNotExist:
            cf_disable_ptr = CustomField.objects.create(
                name="ipaddress_dns_record_disable_ptr",
                description="Disable DNS PTR record generation for this address",
                label="Disable PTR",
                type=CustomFieldTypeChoices.TYPE_BOOLEAN,
                required=False,
                default=False,
                group_name="DNSsync",
                is_cloneable=True,
                weight=300,
            )
            cf_disable_ptr.object_types.set([ipaddress_object_type])
            if options.get("verbosity"):
                self.stdout.write(
                    "Created custom field 'ipaddress_dns_record_disable_ptr'"
                )
