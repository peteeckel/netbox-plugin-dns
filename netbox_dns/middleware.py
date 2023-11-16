from django.db import transaction
from django.db.models import signals
from django.core.exceptions import MiddlewareNotUsed, PermissionDenied, ValidationError

from ipam.models import IPAddress
from ipam.choices import IPAddressStatusChoices

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config
from netbox.signals import post_clean
from utilities.permissions import resolve_permission

from netbox_dns.models import Zone, Record, RecordTypeChoices, RecordStatusChoices


def address_record_cf_data(ip_address):
    name = ip_address.custom_field_data.get("ipaddress_dns_record_name")
    zone_id = ip_address.custom_field_data.get("ipaddress_dns_zone_id")

    if name is None or zone_id is None:
        return None, None

    return name, zone_id


def address_record_type(ip_address):
    return RecordTypeChoices.AAAA if ip_address.family == 6 else RecordTypeChoices.A


def address_record_status(ip_address):
    return (
        RecordStatusChoices.STATUS_ACTIVE
        if ip_address.status == IPAddressStatusChoices.STATUS_ACTIVE
        else RecordStatusChoices.STATUS_INACTIVE
    )


def new_address_record(ip_address):
    name, zone_id = address_record_cf_data(ip_address)

    if zone_id is None:
        return None

    return Record(
        name=name,
        zone_id=zone_id,
        status=address_record_status(ip_address),
        type=address_record_type(ip_address),
        value=str(ip_address.address.ip),
        ipam_ip_address_id=ip_address.id,
        managed=True,
    )


def get_address_record(ip_address):
    return ip_address.netbox_dns_records.first()


def update_address_record(record, ip_address):
    name, zone_id = address_record_cf_data(ip_address)

    record.name = name
    record.zone_id = zone_id
    record.status = address_record_status(ip_address)
    record.value = str(ip_address.address.ip)


def check_address_record(user, record, permission):
    action = resolve_permission(permission)[1]

    if not user.has_perm(permission):
        raise PermissionDenied()

    with transaction.atomic():
        if action in {"add", "change"}:
            record.save()

            queryset = Record.objects.restrict(user=user, action=action)
            if not queryset.filter(pk=record.pk).exists():
                raise PermissionDenied()

        transaction.set_rollback(True)


class Action:
    def __init__(self, request):
        self.request = request

    def post_clean(self, sender, **kwargs):
        ip_address = kwargs.get("instance")
        user = self.request.user

        try:
            if ip_address.id is None:
                #
                # Handle new IP addresses
                #
                record = new_address_record(ip_address)
                if record is not None:
                    check_address_record(user, record, "netbox_dns.add_record")
            else:
                #
                # Handle updates to existing IP addresses
                #
                record = get_address_record(ip_address)
                if record is not None:
                    #
                    # Update or delete the existing address record
                    #
                    name, zone_id = address_record_cf_data(ip_address)
                    if zone_id is not None:
                        #
                        # Update the address record
                        #
                        update_address_record(record, ip_address)
                        check_address_record(user, record, "netbox_dns.change_record")
                    else:
                        #
                        # Delete the address record
                        #
                        check_address_record(user, record, "netbox_dns.delete_record")
                else:
                    #
                    # Create a new address record
                    #
                    record = new_address_record(ip_address)
                    if record is not None:
                        check_address_record(user, record, "netbox_dns.add_record")

        except ValidationError as exc:
            value = exc.error_dict.pop("name", None)
            if value is not None:
                exc.error_dict["cf_ipaddress_dns_record_name"] = value

            value = exc.error_dict.pop("value", None)
            if value is not None:
                exc.error_dict["cf_ipaddress_dns_record_name"] = value

            raise ValidationError(exc)

    #
    # Update DNS related fields according to the contents of the IPAM-DNS
    # coupling custom fields.
    #
    def pre_save(self, sender, **kwargs):
        ip_address = kwargs.get("instance")
        name, zone_id = address_record_cf_data(ip_address)

        if zone_id is not None:
            ip_address.dns_name = f"{name}.{Zone.objects.get(pk=zone_id).name}"
        else:
            ip_address.dns_name = ""
            ip_address.custom_field_data["ipaddress_dns_record_name"] = None
            ip_address.custom_field_data["ipaddress_dns_zone_id"] = None

    #
    # Handle DNS record operation after IPAddress has been created or modified
    #
    def post_save(self, sender, **kwargs):
        ip_address = kwargs.get("instance")
        name, zone_id = address_record_cf_data(ip_address)

        if zone_id is None:
            #
            # Name/Zone CF data has been removed: Remove the DNS address record
            #
            for record in ip_address.netbox_dns_records.all():
                record.delete()

        else:
            #
            # Name/Zone CF data is present: Check for a DNS address record
            # and add or modify it as necessary
            #
            record = get_address_record(ip_address)
            if record is None:
                record = new_address_record(ip_address)
            else:
                update_address_record(record, ip_address)

            record.save()

    #
    # Delete DNS record before deleting IP address
    #
    def pre_delete(self, sender, **kwargs):
        ip_address = kwargs.get("instance")

        for record in ip_address.netbox_dns_records.all():
            user = self.request.user
            check_address_record(user, record, "netbox_dns.delete_record")

            record.delete()


class IpamCouplingMiddleware:
    def __init__(self, get_response):
        if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
            raise MiddlewareNotUsed

        self.get_response = get_response

    def __call__(self, request):
        #
        # Connect signals to actions
        #
        action = Action(request)
        connections = [
            (post_clean, action.post_clean),
            (signals.pre_save, action.pre_save),
            (signals.post_save, action.post_save),
            (signals.pre_delete, action.pre_delete),
        ]
        for signal, receiver in connections:
            signal.connect(receiver, sender=IPAddress)

        response = self.get_response(request)

        for signal, receiver in connections:
            signal.disconnect(receiver)

        return response
