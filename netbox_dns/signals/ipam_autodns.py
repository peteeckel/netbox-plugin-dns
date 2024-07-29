from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, m2m_changed

from netbox.context import current_request
from ipam.models import IPAddress, Prefix

from netbox_dns.models import View
from netbox_dns.utilities import (
    update_dns_records,
    delete_dns_records,
    get_ip_addresses_by_prefix,
    get_ip_addresses_by_view,
)


@receiver(pre_delete, sender=IPAddress)
def ipam_autodns_ipaddress_pre_delete(instance, **kwargs):
    delete_dns_records(instance)


@receiver(post_save, sender=IPAddress)
def ipam_autodns_ipaddress_post_save(instance, **kwargs):
    update_dns_records(instance)


@receiver(post_save, sender=Prefix)
def ipam_autodns_prefix_post_save(instance, **kwargs):
    if kwargs.get("created"):
        return

    for ip_address in get_ip_addresses_by_prefix(instance):
        update_dns_records(ip_address)


@receiver(pre_delete, sender=Prefix)
def ipam_autodns_prefix_pre_delete(instance, **kwargs):
    """
    Workaround for an ancient Django bug (https://code.djangoproject.com/ticket/17688)
    """
    # +
    # If the deletion happens via API or GUI, there is a request object and
    # NetBox handles this itself as part of handle_deleted_object() in
    # netbox/extras/signals.py, so we don't need to do anything here to avoid
    # triggering m2m_changed multiple times.
    # -
    if current_request.get() is not None:
        return

    # +
    # Explicitly remove the relation so the m2m_changed signal is sent by the
    # View model relation to Prefix
    # -
    for view in instance.netbox_dns_views.all():
        view.snapshot()
        view.prefixes.remove(instance)


@receiver(m2m_changed, sender=View.prefixes.through)
def ipam_autodns_view_prefix_changed(**kwargs):
    if kwargs.get("action") not in ("post_add", "post_remove"):
        return

    for prefix in Prefix.objects.filter(pk__in=kwargs.get("pk_set")):
        for ip_address in get_ip_addresses_by_prefix(prefix):
            update_dns_records(ip_address)
