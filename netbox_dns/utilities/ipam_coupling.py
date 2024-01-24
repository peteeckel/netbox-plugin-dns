from ipam.choices import IPAddressStatusChoices
from utilities.permissions import resolve_permission

from netbox_dns.models import Record, RecordTypeChoices, RecordStatusChoices

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config


class DNSPermissionDenied(Exception):
    pass


def ipaddress_cf_data(ip_address):
    name = ip_address.custom_field_data.get("ipaddress_dns_record_name")
    ttl = ip_address.custom_field_data.get("ipaddress_dns_record_ttl")
    disable_ptr = ip_address.custom_field_data.get("ipaddress_dns_record_disable_ptr")
    if disable_ptr is None:
        disable_ptr = False
    zone_id = ip_address.custom_field_data.get("ipaddress_dns_zone_id")

    if name is None or zone_id is None:
        return None, None, False, None

    return name, ttl, disable_ptr, zone_id


def address_record_type(ip_address):
    return RecordTypeChoices.AAAA if ip_address.family == 6 else RecordTypeChoices.A


def address_record_status(ip_address):
    ip_active_status_list = get_plugin_config(
        "netbox_dns",
        "ipam_coupling_ip_active_status_list",
        (
            IPAddressStatusChoices.STATUS_ACTIVE,
            IPAddressStatusChoices.STATUS_DHCP,
            IPAddressStatusChoices.STATUS_SLAAC,
        ),
    )

    return (
        RecordStatusChoices.STATUS_ACTIVE
        if ip_address.status in ip_active_status_list
        else RecordStatusChoices.STATUS_INACTIVE
    )


def get_address_record(ip_address):
    return ip_address.netbox_dns_records.first()


def new_address_record(instance):
    name, ttl, disable_ptr, zone_id = ipaddress_cf_data(instance)

    if zone_id is None:
        return None

    return Record(
        name=name,
        zone_id=zone_id,
        ttl=ttl,
        disable_ptr=disable_ptr,
        status=address_record_status(instance),
        type=address_record_type(instance),
        value=str(instance.address.ip),
        ipam_ip_address_id=instance.id,
        managed=True,
    )


def update_address_record(record, ip_address):
    name, ttl, disable_ptr, zone_id = ipaddress_cf_data(ip_address)

    record.name = name
    record.ttl = ttl
    record.disable_ptr = disable_ptr
    record.zone_id = zone_id
    record.status = address_record_status(ip_address)
    record.value = str(ip_address.address.ip)


def check_permission(request, permission, record=None):
    if record is not None and record.pk is None:
        check_record = None
    else:
        check_record = record

    user = request.user

    if not user.has_perm(permission, check_record):
        action = resolve_permission(permission)[1]
        item = "records" if check_record is None else f"record {check_record}"

        raise DNSPermissionDenied(f"User {user} is not allowed to {action} DNS {item}")


def dns_changed(old, new):
    return any(
        (
            old.address.ip != new.address.ip,
            old.custom_field_data.get("ipaddress_dns_record_name")
            != new.custom_field_data.get("ipaddress_dns_record_name"),
            old.custom_field_data.get("ipaddress_dns_record_ttl")
            != new.custom_field_data.get("ipaddress_dns_record_ttl"),
            old.custom_field_data.get("ipaddress_dns_record_disable_ptr")
            != new.custom_field_data.get("ipaddress_dns_record_disable_ptr"),
            old.custom_field_data.get("ipaddress_dns_zone_id")
            != new.custom_field_data.get("ipaddress_dns_zone_id"),
        )
    )
