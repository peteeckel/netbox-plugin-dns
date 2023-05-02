from extras.plugins import PluginConfig

__version__ = "0.18.0-beta1"


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = "Netbox DNS"
    description = "Netbox DNS"
    min_version = "3.5"
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
    }
    base_url = "netbox-dns"


config = DNSConfig
