from django.core.exceptions import ValidationError


def validate_prefix(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError(
            f"{prefix} is not a valid prefix. Did you mean {prefix.cidr}?"
        )


def validate_ipv4(prefix):
    if prefix.version != 4:
        raise ValidationError(f"RFC2317 requires an IPv4 prefix.")


def validate_rfc2317(prefix):
    if prefix.prefixlen <= 24:
        raise ValidationError(f"RFC2317 requires at least 25 bit prefix length.")
