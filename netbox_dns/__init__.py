from extras.plugins import PluginConfig

__version__ = "0.6.0"


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = "Netbox DNS"
    description = "Netbox DNS"
    min_version = "3.0.0"
    max_version = None
    version = __version__
    author = "Aurora Research Lab"
    author_email = "info@aurorabilisim.com"
    required_settings = []
    default_settings = {
        "zone_default_ttl": 86400,
        "zone_soa_serial_auto": True,
        "zone_soa_serial": 1,
        "zone_soa_refresh": 172800,
        "zone_soa_retry": 7200,
        "zone_soa_expire": 2592000,
        "zone_soa_minimum": 3600,
    }


config = DNSConfig
