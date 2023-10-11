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
        name = ip.custom_field_data.get("name")
        zone_id = ip.custom_field_data.get("zone")

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
        name = ip.custom_field_data.get("name")
        zone_id = ip.custom_field_data.get("zone")
        zone = Zone.objects.get(id=zone_id) if zone_id else None

        # Clear the other field if one is empty, which is inconsistent
        if (name and not zone) or (zone and not name):
            zone = name = None

        # Delete DNS record because name and zone have been removed
        if name == zone == None:
            # Get current dns record
            if record_id := ip.custom_field_data.get("dns_record"):
                record = Record.objects.get(id=record_id)
                # Clear all custom fields related to DNS if permission ok
                check_record_permission(user, record, "netbox_dns.delete_record")

                ip.dns_name = ""
                ip.custom_field_data["dns_record"] = None
                ip.custom_field_data["name"] = ""
                ip.custom_field_data["zone"] = None
                ip.save(update_fields=["custom_field_data", "dns_name"])
                record.delete()

        # Modify or add DNS record
        else:
            # Does the object already have a DNS record ?
            # Modify DNS record
            if record_id := ip.custom_field_data.get("dns_record"):
                record = Record.objects.get(id=record_id)
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
                # Fetch an existing (unmanaged) DNS record or create a new one
                type = RecordTypeChoices.AAAA if ip.family == 6 else RecordTypeChoices.A
                value = str(ip.address.ip)
                try:
                    record = Record.objects.get(
                        name=name, zone=zone, value=value, type=type, managed=False
                    )
                    record.managed = True
                except:
                    record = Record(
                        name=name,
                        zone=zone,
                        type=type,
                        value=value,
                        managed=True,
                    )

                check_record_permission(
                    user, record, "netbox_dns.add_record", commit=True
                )
                # Link record to IP Address
                ip.custom_field_data["dns_record"] = record.id
                # cosmetic: update dns_name field with FQDN
                ip.dns_name = f"{name}.{zone.name}"
                # Save modified field in IP after creating record
                ip.save(update_fields=["custom_field_data", "dns_name"])

    #
    # Delete DNS record before deleting IP address
    #
    def pre_delete(self, sender, **kwargs):
        # Get IPAddress instance
        ip = kwargs.get("instance")
        # Get DNS record if any
        record_id = ip.custom_field_data.get("dns_record")
        if record_id:
            # Delete DNS record if it already exists
            record = Record.objects.get(id=record_id)
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
