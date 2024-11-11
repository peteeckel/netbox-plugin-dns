from netaddr import IPAddress, IPNetwork, AddrFormatError

from django.core.management.base import BaseCommand

from netbox_dns.models import Zone, Record
from netbox_dns.choices import ZoneStatusChoices, RecordTypeChoices


def zone_rename_passive_status_to_parked(verbose=False):
    passive_zones = Zone.objects.filter(status="passive")
    if passive_zones:
        if verbose:
            print("Renaming 'passive' zone status to 'parked'")

        for zone in passive_zones:
            zone.status = ZoneStatusChoices.STATUS_PARKED
            zone.save()


def zone_cleanup_ns_records(verbose=False):
    ns_name = "@"

    for zone in Zone.objects.all():
        nameservers = zone.nameservers.all()
        nameserver_names = [f'{ns.name.rstrip(".")}.' for ns in nameservers]

        delete_ns = zone.records.filter(
            name=ns_name, type=RecordTypeChoices.NS
        ).exclude(value__in=nameserver_names)
        for record in delete_ns:
            if verbose:
                print(f"Deleting obsolete NS record {record}")
            record.delete()

        for ns in nameserver_names:
            ns_records = zone.records.filter(
                name=ns_name,
                type=RecordTypeChoices.NS,
                value=ns,
            )

            delete_ns = ns_records[1:]
            for record in delete_ns:
                if verbose:
                    print(f"Deleting duplicate NS record {record}")
                record.delete()

            try:
                ns_record = zone.records.get(
                    name=ns_name,
                    type=RecordTypeChoices.NS,
                    value=ns,
                )

                if ns_record.ttl is not None or not ns_record.managed:
                    if verbose:
                        print(f"Updating NS record '{ns_record}'")
                    ns_record.ttl = None
                    ns_record.managed = True
                    ns_record.save()

            except Record.DoesNotExist:
                if verbose:
                    print(f"Creating NS record for '{ns.rstrip('.')}' in zone '{zone}'")
                Record.objects.create(
                    name=ns_name,
                    zone=zone,
                    type=RecordTypeChoices.NS,
                    value=ns,
                    ttl=None,
                    managed=True,
                )


def zone_update_soa_records(verbose=False):
    soa_name = "@"

    for zone in Zone.objects.all():
        delete_soa = zone.records.filter(name=soa_name, type=RecordTypeChoices.SOA)[1:]
        for record in delete_soa:
            if verbose:
                print(f"Deleting duplicate SOA record {record}")
            record.delete()

        zone.update_soa_record()


def zone_update_arpa_network(verbose=False):
    for zone in Zone.objects.filter(name__endswith=".arpa"):
        name = zone.name

        # TODO: Rewrite with utility function
        if name.endswith(".in-addr.arpa"):
            address = ".".join(reversed(name.replace(".in-addr.arpa", "").split(".")))
            mask = len(address.split(".")) * 8

            try:
                prefix = IPNetwork(f"{address}/{mask}")
            except AddrFormatError:
                prefix = None

        elif name.endswith("ip6.arpa"):
            address = "".join(reversed(name.replace(".ip6.arpa", "").split(".")))
            mask = len(address)
            address = address + "0" * (32 - mask)

            try:
                prefix = IPNetwork(
                    f"{':'.join([(address[i:i+4]) for i in range(0, 32, 4)])}/{mask*4}"
                )
            except AddrFormatError:
                prefix = None
        # TODO: End

        if zone.arpa_network != prefix:
            if verbose:
                print(f"Updating ARPA prefix for zone '{zone}' to '{prefix}'")
            zone.arpa_network = prefix
            zone.save()


def record_cleanup_disable_ptr(verbose=False):
    Record.objects.filter(
        disable_ptr=False,
    ).exclude(
        type__in=(RecordTypeChoices.A, RecordTypeChoices.AAAA)
    ).update(disable_ptr=True)


def record_update_ptr_records(verbose=False):
    for record in Record.objects.filter(
        type__in=(RecordTypeChoices.A, RecordTypeChoices.AAAA)
    ):
        record.save(update_fields=["ptr_record"])


def record_update_ip_address(verbose=False):
    for record in Record.objects.filter(
        type__in=(RecordTypeChoices.A, RecordTypeChoices.AAAA, RecordTypeChoices.PTR)
    ):
        if record.is_ptr_record:
            if record.ip_address != record.address_from_name:
                if verbose:
                    print(
                        f"Updating IP address of pointer record {record} to {record.address_from_name}"
                    )
                record.ip_address = record.address_from_name
                record.save()
        else:
            if record.ip_address != IPAddress(record.value):
                if verbose:
                    print(
                        f"Updating IP address of address record {record} to {IPAddress(record.value)}"
                    )
                record.ip_address = record.value
                record.save()


class Command(BaseCommand):
    help = "Clean up NetBox DNS database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose", action="store_true", help="Increase output verbosity"
        )

    def handle(self, *model_names, **options):
        zone_rename_passive_status_to_parked(options["verbose"])
        zone_cleanup_ns_records(options["verbose"])
        zone_update_soa_records(options["verbose"])
        zone_update_arpa_network(options["verbose"])
        record_cleanup_disable_ptr(options["verbose"])
        record_update_ptr_records(options["verbose"])
        record_update_ip_address(options["verbose"])

        self.stdout.write("Database cleanup completed.")
