from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from netbox.plugins import PluginConfig
from netbox.plugins.utils import get_plugin_config
from ipam.choices import IPAddressStatusChoices

from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices, ZoneStatusChoices

__version__ = "1.2b1"


def _check_list(setting):
    if not isinstance(get_plugin_config("netbox_dns", setting), list):
        raise ImproperlyConfigured(f"{setting} must be a list")


class DNSConfig(PluginConfig):
    name = "netbox_dns"
    verbose_name = _("NetBox DNS")
    description = _("NetBox plugin for DNS data")
    min_version = "4.2.0"
    version = __version__
    author = "Peter Eckel"
    author_email = "pete@netbox-dns.org"
    required_settings = []
    default_settings = {
        "zone_default_ttl": 86400,
        "zone_soa_ttl": 86400,
        "zone_soa_serial": 1,
        "zone_soa_refresh": 43200,
        "zone_soa_retry": 7200,
        "zone_soa_expire": 2419200,
        "zone_soa_minimum": 3600,
        "zone_active_status": [
            ZoneStatusChoices.STATUS_ACTIVE,
            ZoneStatusChoices.STATUS_DYNAMIC,
        ],
        "record_active_status": [
            RecordStatusChoices.STATUS_ACTIVE,
        ],
        "dnssync_disabled": False,
        "dnssync_ipaddress_active_status": [
            IPAddressStatusChoices.STATUS_ACTIVE,
            IPAddressStatusChoices.STATUS_DHCP,
            IPAddressStatusChoices.STATUS_SLAAC,
        ],
        "dnssync_conflict_deactivate": False,
        "dnssync_minimum_zone_labels": 2,
        "tolerate_characters_in_zone_labels": "",
        "tolerate_underscores_in_labels": False,
        "tolerate_underscores_in_hostnames": False,  # Deprecated, will be removed in 1.2.0
        "tolerate_leading_underscore_types": [
            RecordTypeChoices.SRV,
            RecordTypeChoices.TLSA,
            RecordTypeChoices.TXT,
        ],
        "tolerate_non_rfc1035_types": [],
        "enable_root_zones": False,
        "enforce_unique_records": True,
        "enforce_unique_rrset_ttl": True,
        "menu_name": "DNS",
        "top_level_menu": True,
    }
    base_url = "netbox-dns"

    def ready(self):
        super().ready()

        if not get_plugin_config("netbox_dns", "dnssync_disabled"):
            import netbox_dns.signals.ipam_dnssync  # noqa: F401
            import netbox_dns.tables.ipam_dnssync  # noqa: F401

        for setting in (
            "zone_active_status",
            "record_active_status",
            "dnssync_ipaddress_active_status",
            "tolerate_leading_underscore_types",
        ):
            _check_list(setting)

        # +
        # TODO: Remove this workaround as soon as it's no longer required
        #
        # Force loading views so the register_model_view is run for all views
        # -
        import netbox_dns.views  # noqa: F401


#
# Initialize plugin config
#
config = DNSConfig
