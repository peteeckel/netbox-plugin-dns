from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


__all__ = (
    "validate_prefix",
    "validate_ipv4",
    "validate_rfc2317",
)


def validate_prefix(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError(
            _("{prefix} is not a valid prefix. Did you mean {cidr}?").format(
                prefix=prefix, cidr=prefix.cidr
            )
        )


def validate_ipv4(prefix):
    if prefix.version != 4:
        raise ValidationError(_("RFC2317 requires an IPv4 prefix."))


def validate_rfc2317(prefix):
    if prefix.prefixlen <= 24:
        raise ValidationError(_("RFC2317 requires at least 25 bit prefix length."))
