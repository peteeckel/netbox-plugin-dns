from django.db import transaction
from django.db.models import signals
from django.core.exceptions import MiddlewareNotUsed, PermissionDenied

from ipam.models.ip import IPAddress
from extras.plugins import get_plugin_config
from netbox_dns.models import Zone, Record, RecordTypeChoices
from utilities.exceptions import PermissionsViolation, AbortRequest
from utilities.permissions import resolve_permission


class Action:
    def __init__(self, request):
        self.request = request

    #
    # Check permission to create DNS record before IP address creation
    # NB: If IP address is created *before* DNS record is allowed it's too late
    # → permission check must be done at pre-save, and an exception
    # must be raised to prevent IP creation.
    #
    def pre_save(self, sender, **kwargs):
        if kwargs.get("update_fields"):
            return

        ip = kwargs.get("instance")
        name = ip.custom_field_data.get("ipaddress_dns_record_name")
        zone_id = ip.custom_field_data.get("ipaddress_dns_zone_id")

        # Handle new IP Address only; name and zone must both be defined
        if ip.id is None and name and zone_id:
            zone = Zone.objects.get(id=zone_id)
            if ip.family == 6:
                type = RecordTypeChoices.AAAA
            else:
                type = RecordTypeChoices.A
            value = str(ip.address.ip)

            # Create a DNS record *without saving* in order to check permissions
            record = Record(name=name, zone=zone, type=type, value=value)
            user = self.request.user
            check_record_permission(user, record, "netbox_dns.add_record")

    #
    # Handle DNS record operation after IPAddress has been created or modified
    #
    def post_save(self, sender, **kwargs):
        # Do not process specific field update (eg. dns_hostname modify)
        if kwargs.get("update_fields"):
            return

        user = self.request.user
        ip = kwargs.get("instance")
        name = ip.custom_field_data.get("ipaddress_dns_record_name")
        zone_id = ip.custom_field_data.get("ipaddress_dns_zone_id")
        zone = Zone.objects.get(id=zone_id) if zone_id else None

        # Clear the other field if one is empty, which is inconsistent
        if (name and not zone) or (zone and not name):
            zone = name = None

        # Delete DNS record because name and zone have been removed
        if name == zone == None:
            # Find the record pointing to this IP Address
            for record in Record.objects.filter(ipam_ip_address=ip):
                # If permission ok, clear all fields related to DNS
                check_record_permission(user, record, "netbox_dns.delete_record")
                ip.dns_name = ""
                ip.custom_field_data["ipaddress_dns_record_name"] = ""
                ip.custom_field_data["ipaddress_dns_zone_id"] = None
                ip.save(update_fields=["custom_field_data", "dns_name"])
                record.delete()

        # Modify or add DNS record
        else:
            # If DNS record already point to this IP, modify it
            query = Record.objects.filter(ipam_ip_address=ip)
            if query.count() != 0:
                record = query[0]
                record.name, record.zone = name, zone
                record.value = str(ip.address.ip)
                record.type = (
                    RecordTypeChoices.AAAA if ip.family == 6 else RecordTypeChoices.A
                )
                check_record_permission(user, record, "netbox_dns.change_record")
                record.save()
                # Update dns_name field with FQDN
                ip.dns_name = f"{name}.{zone.name}"
                ip.save(update_fields=["dns_name"])
            else:
                # Create a new record
                type = RecordTypeChoices.AAAA if ip.family == 6 else RecordTypeChoices.A
                record = Record(
                    name=name,
                    zone=zone,
                    type=type,
                    value=str(ip.address.ip),
                    ipam_ip_address=ip,
                    managed=True,
                )
                check_record_permission(
                    user, record, "netbox_dns.add_record", commit=True
                )
                # cosmetic: update dns_name field with FQDN
                ip.dns_name = f"{name}.{zone.name}"
                # Save modified field in IP after creating record
                ip.save(update_fields=["dns_name"])

    #
    # Delete DNS record before deleting IP address
    #
    def pre_delete(self, sender, **kwargs):
        # Get IPAddress instance
        ip = kwargs.get("instance")
        for record in Record.objects.filter(ipam_ip_address=ip):
            user = self.request.user
            check_record_permission(user, record, "netbox_dns.delete_record")
            record.delete()


#
# Filter through permissions. Simulate adding the record in the "add" case.
# NB: Side-effect if "commit" is set to True → the DNS record is created.
# This is necessary to avoid the cascading effects of PTR creation.
#
def check_record_permission(user, record, perm, commit=False):
    # Check that the user has been granted the required permission(s).
    action = resolve_permission(perm)[1]

    if not user.has_perm(perm):
        raise PermissionDenied()

    try:
        with transaction.atomic():
            # Save record when adding
            # Rollback is done at the end of the transaction, unless committed

            if action == "add":
                record.save()

            # Update the view's QuerySet to filter only the permitted objects
            queryset = Record.objects.all()
            queryset = queryset.restrict(user, action)
            # Check that record conforms to permissions
            # → must be included in the restricted queryset
            if not queryset.filter(pk=record.pk).exists():
                raise PermissionDenied()

            if not commit:
                raise AbortRequest("Normal Exit")

    # Catch "Normal Exit" without modification, rollback transaction
    except AbortRequest as e:
        pass

    except Exception as e:
        raise e


class IpamCouplingMiddleware:
    def __init__(self, get_response):
        if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
            raise MiddlewareNotUsed

        self.get_response = get_response

    def __call__(self, request):
        # connect signals to actions
        action = Action(request)
        connections = [
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
