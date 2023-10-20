from extras.plugins import PluginConfig
import logging

logger = logging.getLogger("netbox.config")

__version__ = "0.20.1"


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = "NetBox DNS"
    description = "NetBox plugin for DNS data"
    min_version = "3.5.8"
    version = __version__
    author = "Peter Eckel"
    author_email = "pe-netbox-plugin-dns@hindenburgring.com"
    middleware = ["netbox_dns.middleware.IpamCouplingMiddleware"]
    required_settings = []
    default_settings = {
        "zone_default_ttl": 86400,
        "zone_soa_serial_auto": True,
        "zone_soa_serial": 1,
        "zone_soa_refresh": 172800,
        "zone_soa_retry": 7200,
        "zone_soa_expire": 2592000,
        "zone_soa_minimum": 3600,
        "feature_ipam_coupling": False,
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

    def ready(self):
        #
        # Check if required custom field exist for IPAM coupling
        #
        if self.default_settings["feature_ipam_coupling"]:
            from extras.models import CustomField
            from ipam.models import IPAddress
            from django.contrib.contenttypes.models import ContentType

            objtype = ContentType.objects.get_for_model(IPAddress)
            required_cf = ("ipaddress_dns_record_name", "ipaddress_dns_zone_id")

            if CustomField.objects.filter(
                name__in=required_cf, content_types=objtype
            ).count() < len(required_cf):
                logger.warning(
                    "'feature_ipam_coupling' is enabled, but the required custom"
                    " fields for IPAM-DNS coupling are missing. Please run the"
                    " Django management command 'setup_coupling' to create the"
                    " custom fields."
                )

        super().ready()


#
# Initialize plugin config
#
config = DNSConfig
