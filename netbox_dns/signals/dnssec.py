from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError

from netbox.context import current_request
from utilities.exceptions import AbortRequest

from netbox_dns.validators import validate_key_template_assignment

from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate


@receiver(m2m_changed, sender=DNSSECPolicy.key_templates.through)
def dnssec_policy_key_templates_changed(action, instance, pk_set, **kwargs):
    request = current_request.get()

    key_templates = instance.key_templates.all()
    match action:
        case "pre_remove":
            key_templates = key_templates.exclude(pk__in=pk_set)
        case "pre_add":
            key_templates |= DNSSECKeyTemplate.objects.filter(pk__in=pk_set)
        case _:
            return

    try:
        validate_key_template_assignment(key_templates)
    except ValidationError as exc:
        if request is not None:
            raise AbortRequest(exc)
        else:
            raise exc
