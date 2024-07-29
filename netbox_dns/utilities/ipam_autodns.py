import re

from collections import defaultdict

from dns import name as dns_name

from django.db.models import Q

from ipam.models import IPAddress, Prefix

from netbox_dns.models import zone as _zone
from netbox_dns.models import record as _record


__all__ = (
    "get_zones",
    "update_dns_records",
    "delete_dns_records",
    "get_ip_addresses_by_prefix",
    "get_ip_addresses_by_view",
    "get_ip_addresses_by_zone",
)


def _get_assigned_views(ip_address):
    longest_prefix = Prefix.objects.filter(
        vrf=ip_address.vrf,
        prefix__net_contains_or_equals=str(ip_address.address.ip),
        netbox_dns_views__isnull=False,
    ).last()

    if longest_prefix is None:
        return []

    return longest_prefix.netbox_dns_views.all()


def get_zones(ip_address):
    views = _get_assigned_views(ip_address)
    if not views:
        return []

    fqdn = dns_name.from_text(ip_address.dns_name)
    zone_name_candidates = [
        fqdn.split(i)[1].to_text().rstrip(".") for i in range(3, len(fqdn.labels))
    ]

    zones = _zone.Zone.objects.filter(
        view__in=views,
        name__in=zone_name_candidates,
        active=True,
    )

    if not zones:
        return []

    zone_map = defaultdict(list)
    for zone in zones:
        zone_map[zone.view].append(zone)

    return [
        sorted(zones_per_view, key=lambda x: len(x.name))[-1]
        for zones_per_view in zone_map.values()
    ]


def update_dns_records(ip_address):
    if ip_address.dns_name == "":
        delete_dns_records(ip_address)
        return

    zones = get_zones(ip_address)

    for record in ip_address.netbox_dns_records.all():
        if record.zone not in zones:
            record.delete()
            continue

        if record.fqdn != ip_address.dns_name or record.value != ip_address.address.ip:
            record.update_from_ip_address(ip_address)

    for zone in set(zones).difference(
        {record.zone for record in ip_address.netbox_dns_records.all()}
    ):
        _record.Record.create_from_ip_address(ip_address, zone)


def delete_dns_records(ip_address):
    for record in ip_address.netbox_dns_records.all():
        record.delete()


def get_ip_addresses_by_prefix(prefix):
    """
    Find all IPAddress objects that are in a given prefix, provided that prefix
    is assigned to NetBox DNS view. IPAddress objects belonging to a sub-prefix
    that is assigned to a NetBox DNS view itself are excluded, because the zones
    that are relevant for them are depending on the view set of the sub-prefix.

    If neither the prefix nor any parent prefix is assigned to a view, the list
    of IPAddress objects returned is empty.
    """
    if not (
        Prefix.objects.filter(
            vrf=prefix.vrf, prefix__net_contains_or_equals=prefix.prefix
        )
        .exclude(netbox_dns_views__isnull=True)
        .exists()
    ):
        return IPAddress.objects.none()

    queryset = IPAddress.objects.filter(
        vrf=prefix.vrf, address__net_host_contained=prefix.prefix
    )

    for exclude_child in prefix.get_child_prefixes().filter(
        netbox_dns_views__isnull=False
    ):
        queryset = queryset.exclude(
            vrf=exclude_child.vrf,
            address__net_host_contained=exclude_child.prefix,
        )

    return queryset


def get_ip_addresses_by_view(view):
    """
    Find all IPAddress objects that are within prefixes that have a NetBox DNS
    view assigned to them, or that inherit a view from their parent prefix.

    Inheritance is defined recursively if the prefix is assigned to the view or
    if it is a child prefix of the prefix that is not assigned to a view directly
    or by inheritance.
    """
    queryset = IPAddress.objects.none()
    for prefix in Prefix.objects.filter(netbox_dns_views__in=[view]):
        sub_queryset = IPAddress.objects.filter(
            vrf=prefix.vrf, address__net_host_contained=prefix.prefix
        )
        for exclude_child in prefix.get_child_prefixes().exclude(
            Q(netbox_dns_views__isnull=True) | Q(netbox_dns_views__in=[view])
        ):
            sub_queryset = sub_queryset.exclude(
                vrf=exclude_child.vrf,
                address__net_host_contained=exclude_child.prefix,
            )
        queryset |= sub_queryset

    return queryset


def get_ip_addresses_by_zone(zone):
    """
    Find all IPAddress objects that are relevant for a NetBox DNS zone. These
    are the IPAddress objects in prefixes assigned to the same view, if the
    'dns_name' attribute of the IPAddress object ends in the zone's name.
    """
    queryset = get_ip_addresses_by_view(zone.view)

    return queryset.filter(dns_name__regex=rf"\.{re.escape(zone.name)}\.?$")
