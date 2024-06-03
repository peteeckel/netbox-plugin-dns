import re

from django.core.exceptions import ValidationError

from netbox.plugins.utils import get_plugin_config

LABEL = r"[a-z0-9][a-z0-9-]*(?<!-)"
TOLERANT_LABEL = r"[a-z0-9][a-z0-9-_]*(?<![-_])"
LEADING_UNDERSCORE_LABEL = r"[a-z0-9_][a-z0-9-]*(?<!-)"
TOLERANT_LEADING_UNDERSCORE_LABEL = r"[a-z0-9_][a-z0-9-_]*(?<![-_])"


def has_invalid_double_dash(name):
    return bool(re.findall(r"\b(?!xn)..--", name, re.IGNORECASE))


def validate_fqdn(name, always_tolerant=False):
    if always_tolerant or get_plugin_config(
        "netbox_dns", "tolerate_underscores_in_hostnames"
    ):
        regex = rf"^(\*|{TOLERANT_LABEL})(\.{TOLERANT_LABEL})+\.?$"
    else:
        regex = rf"^(\*|{LABEL})(\.{LABEL})+\.?$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"{name} is not a valid fully qualified DNS host name")


def validate_extended_hostname(
    name, tolerate_leading_underscores=False, always_tolerant=False
):
    if always_tolerant or tolerate_leading_underscores:
        if always_tolerant or get_plugin_config(
            "netbox_dns", "tolerate_underscores_in_hostnames"
        ):
            regex = rf"^([*@]|(\*\.)?{TOLERANT_LEADING_UNDERSCORE_LABEL}(\.{TOLERANT_LEADING_UNDERSCORE_LABEL})*\.?)$"
        else:
            regex = rf"^([*@]|(\*\.)?{LEADING_UNDERSCORE_LABEL}(\.{LEADING_UNDERSCORE_LABEL})*\.?)$"
    elif get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
        regex = rf"^([*@]|(\*\.)?{TOLERANT_LABEL}(\.{TOLERANT_LABEL})*\.?)$"
    else:
        regex = rf"^([*@]|(\*\.)?{LABEL}(\.{LABEL})*\.?)$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"{name} is not a valid DNS host name")


def validate_domain_name(name, always_tolerant=False, allow_empty_label=False):
    if name == "@" and allow_empty_label:
        return

    if name == "." and (
        always_tolerant or get_plugin_config("netbox_dns", "enable_root_zones")
    ):
        return

    if always_tolerant:
        regex = rf"^{TOLERANT_LEADING_UNDERSCORE_LABEL}(\.{TOLERANT_LEADING_UNDERSCORE_LABEL})*\.?$"
    elif get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
        regex = rf"^{TOLERANT_LABEL}(\.{TOLERANT_LABEL})*\.?$"
    else:
        regex = rf"^{LABEL}(\.{LABEL})*\.?$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"{name} is not a valid DNS domain name")
