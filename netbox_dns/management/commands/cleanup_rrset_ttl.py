from django.core.management.base import BaseCommand
from django.db.models import Max, Min

from netbox_dns.models import Record
from netbox_dns.choices import RecordTypeChoices


class Command(BaseCommand):
    help = "Clean up the TTLs for RRSets"

    def add_arguments(self, parser):
        min_max = parser.add_mutually_exclusive_group()
        min_max.add_argument(
            "--min",
            action="store_true",
            help="Use the minimum TTL of an RRSet for all Records",
        )
        min_max.add_argument(
            "--max",
            action="store_true",
            help="Use the maximum TTL of an RRSet for all Records",
        )

    def handle(self, *model_names, **options):
        self.cleanup_rrset_ttl(**options)

        self.stdout.write("RRSet cleanup completed.")

    def cleanup_rrset_ttl(self, **options):
        ttl_records = (
            Record.objects.filter(ttl__isnull=False)
            .exclude(type=RecordTypeChoices.SOA)
            .exclude(type=RecordTypeChoices.PTR, managed=True)
        )
        for record in ttl_records:
            records = Record.objects.filter(
                name=record.name,
                zone=record.zone,
                type=record.type,
            ).exclude(type=RecordTypeChoices.PTR, maanged=True)

            if records.count() == 1:
                if options.get("verbosity") > 2:
                    self.stdout.write(f"Ignoring single record {record.pk} ({record})")
                continue

            if options.get("max"):
                ttl = records.aggregate(Max("ttl")).get("ttl__max")
            else:
                ttl = records.aggregate(Min("ttl")).get("ttl__min")

            for record in records.exclude(ttl=ttl):
                if options.get("verbosity") > 1:
                    self.stdout.write(
                        f"Updating TTL for record {record.pk} ({record}) to {ttl}"
                    )
                record.ttl = ttl
                record.save(update_fields=["ttl"], update_rrset_ttl=False)
