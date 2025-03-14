from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)

__all__ = (
    "validate_key_template",
    "validate_key_template_assignment",
    "validate_key_template_lifetime",
)


def validate_key_template(key_template):
    if key_template.key_size is None:
        return

    if key_template.key_size not in DNSSECKeyTemplateKeySizeChoices.values():
        raise ValidationError(
            {
                "key_size": _("{key_size} is not a supported key size.").format(
                    key_size=key_template.key_size
                )
            }
        )

    if key_template.algorithm != DNSSECKeyTemplateAlgorithmChoices.RSASHA256:
        raise ValidationError(
            {
                "key_size": _(
                    "Specifying the key size is not supported for algorithm {algorithm}."
                ).format(algorithm=key_template.algorithm)
            }
        )


def validate_key_template_assignment(key_templates):
    if key_templates is None:
        return

    csk = key_templates.filter(type=DNSSECKeyTemplateTypeChoices.TYPE_CSK)
    ksk = key_templates.filter(type=DNSSECKeyTemplateTypeChoices.TYPE_KSK)
    zsk = key_templates.filter(type=DNSSECKeyTemplateTypeChoices.TYPE_ZSK)

    if csk and (ksk or zsk):
        raise ValidationError(
            {
                "key_templates": _(
                    "Specifying a CSK together with any other key template type is not allowed."
                )
            }
        )

    if any(
        (
            csk.count() > 1,
            ksk.count() > 1,
            zsk.count() > 1,
        )
    ):
        raise ValidationError(
            {
                "key_templates": _(
                    "At most one key template per type (CSK, KSK and ZSK) is allowed."
                )
            }
        )

    if (ksk and zsk) and (ksk.first().algorithm != zsk.first().algorithm):
        raise ValidationError(
            {"key_templates": _("KSK and ZSK must use the same algorithm.")}
        )


def validate_key_template_lifetime(key_template, policy, raise_exception=True):
    key_lifetime = key_template.lifetime

    if not key_lifetime:
        return

    dnskey_ttl = policy.get_effective_value("dnskey_ttl")
    publish_safety = policy.get_effective_value("publish_safety")
    zone_propagation_delay = policy.get_effective_value("zone_propagation_delay")
    max_zone_ttl = policy.get_effective_value("max_zone_ttl")
    retire_safety = policy.get_effective_value("retire_safety")

    validation_errors = []

    if (
        dnskey_ttl is not None
        and publish_safety is not None
        and zone_propagation_delay is not None
        and key_lifetime < (dnskey_ttl + publish_safety + zone_propagation_delay)
    ):
        validation_errors.append(
            _(
                "Key Lifetime {lifetime} is less than DNSKEY TTL + Publish Safety + Zone Propagation Delay."
            ).format(lifetime=key_lifetime)
        )

    if (
        max_zone_ttl is not None
        and retire_safety is not None
        and zone_propagation_delay is not None
        and key_lifetime < (max_zone_ttl + retire_safety + zone_propagation_delay)
    ):
        validation_errors.append(
            _(
                "Key Lifetime {lifetime} is less than Max Zone TTL + Retire Safety + Zone Propagation Delay."
            ).format(lifetime=key_lifetime)
        )

    if key_template.type == DNSSECKeyTemplateTypeChoices.TYPE_ZSK:
        signatures_validity = policy.get_effective_value("signatures_validity")
        signatures_refresh = policy.get_effective_value("signatures_refresh")

        if (
            signatures_validity is not None
            and signatures_validity is not None
            and key_lifetime < signatures_validity - signatures_refresh
        ):
            validation_errors.append(
                _(
                    "Key Lifetime {lifetime} is less than Signatures Validity - Signatures Refresh."
                )
            ).format(lifetime=key_lifetime)
    else:
        parent_ds_ttl = policy.get_effective_value("parent_ds_ttl")
        parent_propagation_delay = policy.get_effective_value(
            "parent_propagation_delay"
        )

        if (
            parent_ds_ttl is not None
            and retire_safety is not None
            and parent_propagation_delay is not None
            and parent_ds_ttl < retire_safety + parent_propagation_delay
        ):
            validation_errors.append(
                _(
                    "Key Lifetime {lifetime} is less than Parent DS TTL + Retire Safety + Parent Propagation Delay."
                ).format(lifetime=key_lifetime)
            )

    return validation_errors
