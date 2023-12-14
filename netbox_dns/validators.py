import re

from django.core.exceptions import ValidationError

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config

LABEL = r"[a-z0-9][a-z0-9-]*(?<!-)"
TOLERANT_LABEL = r"[a-z0-9][a-z0-9-_]*(?<![-_])"
LEADING_UNDERSCORE_LABEL = r"[a-z0-9_][a-z0-9-]*(?<!-)"
TOLERANT_LEADING_UNDERSCORE_LABEL = r"[a-z0-9_][a-z0-9-_]*(?<![-_])"


def has_invalid_double_dash(name):
    return bool(re.findall(r"\b(?!xn)..--", name, re.IGNORECASE))


def validate_fqdn(name):
    if get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
        regex = rf"^(\*|{TOLERANT_LABEL})(\.{TOLERANT_LABEL})+\.?$"
    else:
        regex = rf"^(\*|{LABEL})(\.{LABEL})+\.?$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"Not a valid fully qualified DNS host name")


def validate_extended_hostname(name, tolerate_leading_underscores=False):
    if tolerate_leading_underscores:
        if get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
            regex = rf"^([*@]|(\*\.)?{TOLERANT_LEADING_UNDERSCORE_LABEL}(\.{TOLERANT_LEADING_UNDERSCORE_LABEL})*\.?)$"
        else:
            regex = rf"^([*@]|(\*\.)?{LEADING_UNDERSCORE_LABEL}(\.{LEADING_UNDERSCORE_LABEL})*\.?)$"
    elif get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
        regex = rf"^([*@]|(\*\.)?{TOLERANT_LABEL}(\.{TOLERANT_LABEL})*\.?)$"
    else:
        regex = rf"^([*@]|(\*\.)?{LABEL}(\.{LABEL})*\.?)$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"Not a valid DNS host name")


def validate_domain_name(name):
    if name == "." and get_plugin_config("netbox_dns", "enable_root_zones"):
        return

    if get_plugin_config("netbox_dns", "tolerate_underscores_in_hostnames"):
        regex = rf"^{TOLERANT_LABEL}(\.{TOLERANT_LABEL})*\.?$"
    else:
        regex = rf"^{LABEL}(\.{LABEL})*\.?$"

    if not re.match(regex, name, flags=re.IGNORECASE) or has_invalid_double_dash(name):
        raise ValidationError(f"Not a valid DNS domain name")
