from netaddr import IPNetwork

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save, post_save, m2m_changed
from django.core.exceptions import ValidationError

from netbox.context import current_request
from netbox.signals import post_clean
from ipam.models import IPAddress, Prefix
from utilities.exceptions import AbortRequest

from netbox_dns.models import view as _view
from netbox_dns.utilities import (
    check_dns_records,
    check_record_permission,
    update_dns_records,
    delete_dns_records,
    get_views_by_prefix,
    get_ip_addresses_by_prefix,
    get_ip_addresses_by_view,
)

AUTODNS_CUSTOM_FIELDS = {
    "ipaddress_dns_disabled": False,
    "ipaddress_dns_record_ttl": None,
    "ipaddress_dns_record_disable_ptr": False,
}

IPADDRESS_ACTIVE_STATUS = settings.PLUGINS_CONFIG["netbox_dns"][
    "autodns_ipaddress_active_status"
]
ENFORCE_UNIQUE_RECORDS = settings.PLUGINS_CONFIG["netbox_dns"]["enforce_unique_records"]


@receiver(post_clean, sender=IPAddress)
def ipam_autodns_ipaddress_post_clean(instance, **kwargs):
    if not isinstance(instance.address, IPNetwork):
        return

    if instance.custom_field_data.get("ipaddress_dns_disabled"):
        return

    # +
    # Check for uniqueness of IP address and dns_name. If unique records are
    # enforced, report an error when trying to create the same IP address with
    # the same dns_name. Ignore existing IP addresses that have their CF
    # "ipaddress_dns_disabled" set to "True".
    # -
    duplicate_addresses = IPAddress.objects.filter(
        address=instance.address,
        vrf=instance.vrf,
        dns_name=instance.dns_name,
        status__in=IPADDRESS_ACTIVE_STATUS,
    )
    if instance.pk is not None:
        duplicate_addresses = duplicate_addresses.exclude(pk=instance.pk)

    if ENFORCE_UNIQUE_RECORDS and instance.status in IPADDRESS_ACTIVE_STATUS:
        for ip_address in duplicate_addresses.only("custom_field_data"):
            if not ip_address.custom_field_data.get("ipaddress_dns_disabled"):
                raise ValidationError(
                    {
                        "dns_name": "Unique DNS records are enforced and there is already "
                        f"an active IP address {instance.address} with DNS name {instance.dns_name}. "
                        "Plesase choose a different name or disable record creation for this "
                        "IP address."
                    }
                )

    # +
    # Check NetBox DNS record permission for changes to IPAddress custom fields
    #
    # Normally, as the modfication of DNS fields
    if (request := current_request.get()) is not None:
        cf_data = instance.custom_field_data
        if (
            instance.pk is not None
            and any(
                (
                    cf_data.get(cf, cf_default)
                    != IPAddress.objects.get(pk=instance.pk).custom_field_data.get(
                        cf, cf_default
                    )
                    for cf, cf_default in AUTODNS_CUSTOM_FIELDS.items()
                )
            )
            and not check_record_permission()
        ) or (
            instance.pk is None
            and any(
                (
                    cf_data.get(cf, cf_default) != cf_default
                    for cf, cf_default in AUTODNS_CUSTOM_FIELDS.items()
                )
            )
            and not check_record_permission(change=False, delete=False)
        ):
            raise ValidationError(
                f"User '{request.user}' is not allowed to alter AutoDNS custom fields"
            )

    try:
        check_dns_records(instance)
    except ValidationError as exc:
        raise ValidationError({"dns_name": exc.messages})


@receiver(pre_delete, sender=IPAddress)
def ipam_autodns_ipaddress_pre_delete(instance, **kwargs):
    delete_dns_records(instance)


@receiver(pre_save, sender=IPAddress)
def ipam_autodns_ipaddress_pre_save(instance, **kwargs):
    check_dns_records(instance)


@receiver(post_save, sender=IPAddress)
def ipam_autodns_ipaddress_post_save(instance, **kwargs):
    update_dns_records(instance)


@receiver(pre_save, sender=Prefix)
def ipam_autodns_prefix_pre_save(instance, **kwargs):
    """
    Changes that modify the prefix hierarchy cannot be validated properly before
    commiting them. So the solution in this case is to ask the user to deassign
    the prefix from any views it is assigned to and retry.
    """
    request = current_request.get()

    if instance.pk is None or not instance.netbox_dns_views.exists():
        return

    saved_prefix = Prefix.objects.prefetch_related("netbox_dns_views").get(
        pk=instance.pk
    )
    if saved_prefix.prefix != instance.prefix or saved_prefix.vrf != instance.vrf:
        dns_views = ", ".join([view.name for view in instance.netbox_dns_views.all()])
        if request is not None:
            raise AbortRequest(
                f"This prefix is currently assigned to the following DNS views: {dns_views}"
                f"Please deassign it from these views before making changes to the prefix "
                f"or VRF."
            )

        raise ValidationError(
            f"Prefix is assigned to DNS views {dns_views}. Prefix and VRF must not be changed"
        )


@receiver(pre_delete, sender=Prefix)
def ipam_autodns_prefix_pre_delete(instance, **kwargs):
    parent = instance.get_parents().last()
    request = current_request.get()

    if parent is not None and get_views_by_prefix(instance) != get_views_by_prefix(
        parent
    ):
        try:
            for prefix in instance.get_children().filter(
                _depth=instance.depth + 1, netbox_dns_views__isnull=True
            ):
                for ip_address in get_ip_addresses_by_prefix(prefix):
                    check_dns_records(ip_address)
        except ValidationError as exc:
            if request is not None:
                raise AbortRequest(
                    f"Prefix deletion would cause DNS errors: {exc.messages[0]} "
                    "Please review DNS View assignments for this and the parent prefix"
                )
            else:
                raise exc

    # +
    # CAUTION: This only works because the NetBox workaround for an ancient
    # Django bug (see https://code.djangoproject.com/ticket/17688) has already
    # removed the relations between the prefix and the views when this signal
    # handler runs.
    #
    # Should anything be fixed, this code will stop working and need to be
    # revisited.
    #
    # The NetBox workaround only works for requests, not for model level
    # operations. The following code replicates it for non-requests.
    # -
    if request is None:
        for view in instance.netbox_dns_views.all():
            view.snapshot()
            view.prefixes.remove(instance)

    for ip_address in get_ip_addresses_by_prefix(instance):
        update_dns_records(ip_address)


@receiver(m2m_changed, sender=_view.View.prefixes.through)
def ipam_autodns_view_prefix_changed(**kwargs):
    action = kwargs.get("action")
    request = current_request.get()

    # +
    # Handle all post_add and post_remove signals except the ones directly
    # handled by the pre_delete handler for the Prefix model.
    #
    # Yes. This IS ugly.
    # -
    if action not in ("post_add", "post_remove") or (
        request is not None
        and action == "post_remove"
        and (
            request.path.startswith("/ipam/prefixes/")
            or request.path.startswith("/api/ipam/prefixes/")
        )
    ):
        return

    check_view = action != "post_remove"
    for prefix in Prefix.objects.filter(pk__in=kwargs.get("pk_set")):
        for ip_address in get_ip_addresses_by_prefix(prefix, check_view=check_view):
            update_dns_records(ip_address)
