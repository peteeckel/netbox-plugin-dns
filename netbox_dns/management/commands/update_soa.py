from django.core.management.base import BaseCommand

from netbox_dns.models import Zone


class Command(BaseCommand):
    help = "Create or update SOA records for all zones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose", action="store_true", help="Increase output verbosity"
        )

    def handle(self, *model_names, **options):
        zones = Zone.objects.all()

        for zone in zones:
            if options["verbose"]:
                self.stdout.write(f"Updating the SOA record for zone {zone.name}")
            zone.update_soa_record()

        self.stdout.write("All SOA records have been updated")
