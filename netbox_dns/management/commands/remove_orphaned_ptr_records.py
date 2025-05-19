from django.core.management.base import BaseCommand

from netbox_dns.models import Record
from netbox_dns.choices import RecordTypeChoices


class Command(BaseCommand):
    help = "Remove managed PTR records without an address record"

    def handle(self, *model_names, **options):
        orphaned_ptr_records = Record.objects.filter(
            type=RecordTypeChoices.PTR,
            address_records__isnull=True,
            managed=True,
        )

        if not orphaned_ptr_records.exists():
            if options.get("verbosity") >= 1:
                self.stdout.write("No orphaned PTR records found")
            return

        if options.get("verbosity") >= 1:
            self.stdout.write(
                f"Removing {orphaned_ptr_records.count()} orphaned PTR record(s) ..."
            )

        for record in orphaned_ptr_records:
            if options.get("verbosity") >= 2:
                self.stdout.write(
                    f"removing PTR record {record} from zone {record.zone}"
                )
            record.delete()

        if options.get("verbosity") >= 1:
            self.stdout.write("... done.")
