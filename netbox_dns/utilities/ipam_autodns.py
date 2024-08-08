import re

from collections import defaultdict

from dns import name as dns_name

from django.conf import settings
from django.db.models import Q

from netbox.context import current_request
from ipam.models import IPAddress, Prefix

from netbox_dns.models import zone as _zone
from netbox_dns.models import record as _record
from netbox_dns.models import view as _view


__all__ = (
    "get_zones",
    "check_dns_records",
    "update_dns_records",
    "delete_dns_records",
    "get_views_by_prefix",
    "get_ip_addresses_by_prefix",
    "get_ip_addresses_by_view",
    "get_ip_addresses_by_zone",
    "check_record_permission",
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


def _get_record_status(ip_address):
    return (
        RecordStatusChoices.STATE_ACTIVE
        if ip_address.status
        in settings.PLUGINS_CONFIG["netbox_dns"].get(
            "autodns_ipaddress_active_status", []
        )
        else RecordStatusChoices.STATUS_INACTIVE
    )


def _valid_entry(ip_address, zone):
    return zone.view in _get_assigned_views(ip_address) and dns_name.from_text(
        ip_address.dns_name
    ).is_subdomain(dns_name.from_text(zone.name))


def get_zones(ip_address, view=None, old_zone=None):
    if view is None:
        views = _get_assigned_views(ip_address)
        if not views:
            return []

    else:
        views = [view]

    fqdn = dns_name.from_text(ip_address.dns_name)
    zone_name_candidates = [
        fqdn.split(i)[1].to_text().rstrip(".") for i in range(3, len(fqdn.labels))
    ]

    zones = _zone.Zone.objects.filter(
        view__in=views,
        name__in=zone_name_candidates,
        active=True,
    )

    zone_map = defaultdict(list)

    if old_zone is not None:
        zones = zones.exclude(pk=old_zone.pk)
        if _valid_entry(ip_address, old_zone):
            zone_map[old_zone.view].append(old_zone)

    for zone in zones:
        zone_map[zone.view].append(zone)

    return [
        sorted(zones_per_view, key=lambda x: len(x.name))[-1]
        for zones_per_view in zone_map.values()
    ]


def check_dns_records(ip_address, zone=None, view=None):
    if ip_address.dns_name == "":
        return

    if zone is None:
        zones = get_zones(ip_address, view=view)

        if ip_address.pk is not None:
            for record in ip_address.netbox_dns_records.filter(zone__in=zones):
                if (
                    record.fqdn != ip_address.dns_name
                    or record.value != ip_address.address.ip
                    or record.status != _get_record_status(ip_address)
                ):
                    record.update_from_ip_address(ip_address)

                    if record is not None:
                        record.clean()

            zones = _zone.Zone.objects.filter(
                pk__in=[zone.pk for zone in zones]
            ).exclude(
                pk__in=set(
                    ip_address.netbox_dns_records.all().values_list("zone", flat=True)
                )
            )

        for zone in zones:
            record = _record.Record.create_from_ip_address(
                ip_address,
                zone,
            )

            if record is not None:
                record.clean()

    if ip_address.pk is None:
        return

    try:
        new_zone = get_zones(ip_address, old_zone=zone)[0]
    except IndexError:
        return

    for record in ip_address.netbox_dns_records.filter(zone=zone):
        record.update_from_ip_address(ip_address, new_zone)

        if record is not None:
            record.clean(new_zone=new_zone)


def update_dns_records(ip_address):
    if ip_address.dns_name == "":
        delete_dns_records(ip_address)
        return

    zones = get_zones(ip_address)

    if ip_address.pk is not None:
        for record in ip_address.netbox_dns_records.all():
            if record.zone not in zones:
                record.delete()
                continue

            if (
                record.fqdn != ip_address.dns_name
                or record.value != ip_address.address.ip
                or record.status != _get_record_status(ip_address)
            ):
                record.update_from_ip_address(ip_address)

                if record is not None:
                    record.save()

        zones = _zone.Zone.objects.filter(pk__in=[zone.pk for zone in zones]).exclude(
            pk__in=set(
                ip_address.netbox_dns_records.all().values_list("zone", flat=True)
            )
        )

    for zone in zones:
        record = _record.Record.create_from_ip_address(
            ip_address,
            zone,
        )

        if record is not None:
            record.save()


def delete_dns_records(ip_address):
    for record in ip_address.netbox_dns_records.all():
        record.delete()


def get_views_by_prefix(prefix):
    if (views := prefix.netbox_dns_views.all()).exists():
        return views

    if (parent := prefix.get_parents().filter(netbox_dns_views__isnull=False)).exists():
        return parent.last().netbox_dns_views.all()

    return _view.View.objects.none()


def get_ip_addresses_by_prefix(prefix, check_view=True):
    """
    Find all IPAddress objects that are in a given prefix, provided that prefix
    is assigned to NetBox DNS view. IPAddress objects belonging to a sub-prefix
    that is assigned to a NetBox DNS view itself are excluded, because the zones
    that are relevant for them are depending on the view set of the sub-prefix.

    If neither the prefix nor any parent prefix is assigned to a view, the list
    of IPAddress objects returned is empty.
    """
    if check_view and not get_views_by_prefix(prefix):
        return IPAddress.objects.none()

    queryset = IPAddress.objects.filter(
        vrf=prefix.vrf, address__net_host_contained=prefix.prefix
    )

    for exclude_child in prefix.get_children().filter(netbox_dns_views__isnull=False):
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
        for exclude_child in prefix.get_children().exclude(
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


def check_record_permission(add=True, change=True, delete=True):
    checks = locals().copy()

    request = current_request.get()

    if request is None:
        return True

    return all(
        (
            request.user.has_perm(f"netbox_dns.{perm}_record")
            for perm, check in checks.items()
            if check
        )
    )
