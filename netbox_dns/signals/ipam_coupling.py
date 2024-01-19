from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.exceptions import PermissionDenied as APIPermissionDenied

from netbox.signals import post_clean
from netbox.context import current_request
from ipam.models import IPAddress

from netbox_dns.models import Zone
from netbox_dns.utilities.ipam_coupling import (
    ipaddress_cf_data,
    get_address_record,
    new_address_record,
    update_address_record,
    check_permission,
    dns_changed,
    DNSPermissionDenied,
)

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config


@receiver(post_clean, sender=IPAddress)
def ip_address_check_permissions_save(instance, **kwargs):
    if not instance.address:
        return

    if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
        return

    request = current_request.get()
    if request is None:
        return

    try:
        if instance.id is None:
            record = new_address_record(instance)
            if record is not None:
                record.full_clean()
                check_permission(request, "netbox_dns.add_record", record)

        else:
            if not dns_changed(IPAddress.objects.get(pk=instance.id), instance):
                return

            record = get_address_record(instance)
            if record is not None:
                name, ttl, disable_ptr, zone_id = ipaddress_cf_data(instance)
                if zone_id is not None:
                    update_address_record(record, instance)
                    record.full_clean()
                    check_permission(request, "netbox_dns.change_record", record)
                else:
                    check_permission(request, "netbox_dns.delete_record", record)

            else:
                record = new_address_record(instance)
                if record is not None:
                    record.full_clean()
                    check_permission(request, "netbox_dns.add_record", record)

    except ValidationError as exc:
        if hasattr(exc, "error_dict"):
            value = exc.error_dict.pop("name", None)
            if value is not None:
                exc.error_dict["cf_ipaddress_dns_record_name"] = value

            value = exc.error_dict.pop("ttl", None)
            if value is not None:
                exc.error_dict["cf_ipaddress_dns_record_ttl"] = value

            value = exc.error_dict.pop("value", None)
            if value is not None:
                exc.error_dict["cf_ipaddress_dns_record_name"] = value

        raise ValidationError(exc)

    except DNSPermissionDenied as exc:
        raise ValidationError(exc)


@receiver(pre_delete, sender=IPAddress)
def ip_address_delete_address_record(instance, **kwargs):
    if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
        return

    request = current_request.get()
    if request is not None:
        try:
            for record in instance.netbox_dns_records.all():
                check_permission(request, "netbox_dns.delete_record", record)

        except DNSPermissionDenied as exc:
            if request.path_info.startswith("/api/"):
                raise APIPermissionDenied(exc) from None

            raise PermissionDenied(exc) from None

    for record in instance.netbox_dns_records.all():
        record.delete()


#
# Update DNS related fields according to the contents of the IPAM-DNS
# coupling custom fields.
#
@receiver(pre_save, sender=IPAddress)
def ip_address_update_dns_information(instance, **kwargs):
    if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
        return

    name, ttl, disable_ptr, zone_id = ipaddress_cf_data(instance)

    if zone_id is not None:
        instance.dns_name = f"{name}.{Zone.objects.get(pk=zone_id).name}"
    else:
        instance.dns_name = ""
        instance.custom_field_data["ipaddress_dns_record_name"] = None
        instance.custom_field_data["ipaddress_dns_record_ttl"] = None
        instance.custom_field_data["ipaddress_dns_record_disable_ptr"] = False
        instance.custom_field_data["ipaddress_dns_zone_id"] = None


#
# Handle DNS record operation after IPAddress has been created or modified
#
@receiver(post_save, sender=IPAddress)
def ip_address_update_address_record(instance, **kwargs):
    if not get_plugin_config("netbox_dns", "feature_ipam_coupling"):
        return

    name, ttl, disable_ptr, zone_id = ipaddress_cf_data(instance)

    if zone_id is None:
        #
        # Name/Zone CF data has been removed: Remove the DNS address record
        #
        for record in instance.netbox_dns_records.all():
            record.delete()

    else:
        #
        # Name/Zone CF data is present: Check for a DNS address record and add
        # or modify it as necessary
        #
        record = get_address_record(instance)
        if record is None:
            record = new_address_record(instance)
        else:
            update_address_record(record, instance)

        record.save()
