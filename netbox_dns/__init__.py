import sys

from extras.plugins import PluginConfig
from django.db.utils import OperationalError

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config

__version__ = "0.22.9"


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = "NetBox DNS"
    description = "NetBox plugin for DNS data"
    min_version = "3.5.0"
    max_version = "3.99.0"
    version = __version__
    author = "Peter Eckel"
    author_email = "pete@netbox-dns.org"
    required_settings = []
    default_settings = {
        "zone_default_ttl": 86400,
        "zone_soa_serial_auto": True,
        "zone_soa_serial": 1,
        "zone_soa_refresh": 43200,
        "zone_soa_retry": 7200,
        "zone_soa_expire": 2419200,
        "zone_soa_minimum": 3600,
        "feature_ipam_coupling": False,
        "tolerate_underscores_in_hostnames": False,
        "tolerate_leading_underscore_types": [
            "TXT",
            "SRV",
        ],
        "tolerate_non_rfc1035_types": [],
        "enable_root_zones": False,
        "enforce_unique_records": True,
        "enforce_unique_rrset_ttl": True,
    }
    base_url = "netbox-dns"


#
# Initialize plugin config
#
config = DNSConfig
