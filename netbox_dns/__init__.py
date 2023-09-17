from extras.plugins import PluginConfig

__version__ = "0.19.0"


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = "NetBox DNS"
    description = "NetBox plugin for DNS data"
    min_version = "3.5.8"
    version = __version__
    author = "Peter Eckel"
    author_email = "pe-netbox-plugin-dns@hindenburgring.com"
    required_settings = []
    default_settings = {
        "zone_default_ttl": 86400,
        "zone_soa_serial_auto": True,
        "zone_soa_serial": 1,
        "zone_soa_refresh": 172800,
        "zone_soa_retry": 7200,
        "zone_soa_expire": 2592000,
        "zone_soa_minimum": 3600,
        "feature_ipam_integration": False,
        "tolerate_underscores_in_hostnames": False,
        "tolerate_leading_underscore_types": [
            "TXT",
            "SRV",
        ],
        "tolerate_non_rfc1035_types": [],
        "enable_root_zones": False,
        "enforce_unique_records": False,
    }
    base_url = "netbox-dns"


config = DNSConfig
