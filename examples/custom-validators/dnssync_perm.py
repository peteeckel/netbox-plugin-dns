#
# Partial permission validation for the NetBox DNS plugin IPAM DNSsync
# feature.
# When adding or modifying an IP address with dns_name set, check
# for object level permissions for the synced DNS record.
# *No DNS permission is checked when deleting an IP address*
#
# Also *doesn't validate* any other permissions regarding PTR, SOA,
# RFC2317 records etc.
#

from django.db import transaction
from extras.validators import CustomValidator
from netbox.plugins.utils import get_plugin_config
from django.db.models.base import Model


def name_is_allowed(dns_name, ipaddress, request):
    from netbox_dns.models import Record
    from netbox_dns.utilities import get_zones

    # Dnssync is disabled, name is allowed
    if get_plugin_config("netbox_dns", "dnssync_disabled"):
        return True

    # No zone found, name is allowed
    if not (zones := get_zones(ipaddress)):
        return True

    # In a transaction, simulate creating a record in all views/zones
    # and check permission
    allowed = True
    with transaction.atomic():
        savepoint = transaction.savepoint()
        for zone in zones:
            # Create "A" Record
            name = dns_name.replace(zone.name, "")
            value = str(ipaddress.address.ip)
            obj = Record(name=name, zone=zone, type="A", value=value)
            # Low-level save: Record.save() is not called, no additional action
            Model.save(obj)
            # Check object level permissions for user
            queryset = Record.objects.restrict(request.user)
            allowed &= queryset.filter(pk=obj.pk).exists()

        # Rollback all modifications
        transaction.savepoint_rollback(savepoint)

    return allowed


class NamePermissionValidator(CustomValidator):

    def validate(self, ipaddress, request):
        dns_name = ipaddress.dns_name
        if dns_name != "" and not name_is_allowed(dns_name, ipaddress, request):
            self.fail(f"Permission denied on DNS record '{dns_name}'", field="dns_name")
