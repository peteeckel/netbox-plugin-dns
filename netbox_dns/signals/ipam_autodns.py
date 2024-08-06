from netaddr import IPNetwork

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
    update_dns_records,
    delete_dns_records,
    get_views_by_prefix,
    get_ip_addresses_by_prefix,
    get_ip_addresses_by_view,
)


@receiver(post_clean, sender=IPAddress)
def ipam_autodns_ipaddress_post_clean(instance, **kwargs):
    if not isinstance(instance.address, IPNetwork):
        return

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
    commiting them. So the solution in this case is to remove a prefix whose
    VRF or network has changed from all views it currently is assigned to.
    """
    if instance.pk is None or not instance.netbox_dns_views.exists():
        return

    saved_prefix = Prefix.objects.get(pk=instance.pk)
    if saved_prefix.prefix != instance.prefix or saved_prefix.vrf != instance.vrf:
        for view in saved_prefix.netbox_dns_views.all():
            view.prefixes.remove(saved_prefix)


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
