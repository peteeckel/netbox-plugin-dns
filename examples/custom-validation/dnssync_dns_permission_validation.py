#
# Partial permission validation for the NetBox DNS plugin IPAM DNSsync
# feature.
#
# Purpose: when adding or modifying an IP address with dns_name set, check
# for object level permissions for the synced DNS record.
#
# Warning: checks permission only under the following conditions:
# - when adding or modifying an IP address in IPAM (using UI or API),
# - dnssync is not disabled.
# Notably, *no permission are checked when deleting an IP address*
# This is consistent with the idea that IPAM actions have complete
# control over the DNSsync-ed records.
#
# Also *doesn't validate* any other permissions regarding PTR, SOA,
# RFC2317 records etc.
#
# Installation:
#
# Check that CUSTOM_VALIDATORS *is defined* in /opt/netbox/netbox/netbox/configuration.py
#   CUSTOM_VALIDATORS = {}
#
# Copy this script into Netbox local settings:
#   cp dnssync_dns_permission_validation.py /opt/netbox/netbox/netbox/local_settings.py
#
# NB: for local settings to be loaded, at least NetBox v4.0.2 is needed
#

from django.db import transaction, models
from extras.validators import CustomValidator
from netbox.plugins.utils import get_plugin_config, get_installed_plugins
from django.db.models.base import Model


def name_is_allowed(dns_name, ipaddress, request):
    from netbox_dns.models.zone import Zone
    from netbox_dns.models.record import Record
    from netbox_dns.utilities.ipam_dnssync import get_zones

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
            obj = Record(name=name, zone=zone, type="A", value=ipaddress)
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


try:
    from netbox.configuration import CUSTOM_VALIDATORS

    CUSTOM_VALIDATORS["ipam.ipaddress"] = (NamePermissionValidator(),)
except:
    raise ImproperlyConfigured(
        f"Required parameter {CUSTOM_VALIDATORS} missing from configuration."
    )
