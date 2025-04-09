from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from netbox.plugins import PluginConfig
from netbox.plugins.utils import get_plugin_config
from ipam.choices import IPAddressStatusChoices

from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices, ZoneStatusChoices

__version__ = "1.2.7"


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
        "zone_expiration_warning_days": 30,
        "filter_record_types": [],
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
        "tolerate_leading_underscore_types": [
            RecordTypeChoices.CNAME,
            RecordTypeChoices.DNAME,
            RecordTypeChoices.SRV,
            RecordTypeChoices.SVCB,
            RecordTypeChoices.TLSA,
            RecordTypeChoices.TXT,
        ],
        "tolerate_non_rfc1035_types": [],
        "enable_root_zones": False,
        "enforce_unique_records": True,
        "enforce_unique_rrset_ttl": True,
        "menu_name": "DNS",
        "top_level_menu": True,
        "convert_names_to_lowercase": False,
        "dnssec_purge_keys": 7776000,  # P90D
        "dnssec_publish_safety": 3600,  # PT1H
        "dnssec_retire_safety": 3600,  # PT1H
        "dnssec_signatures_jitter": 43200,  # PT12H
        "dnssec_signatures_refresh": 432000,  # P5D
        "dnssec_signatures_validity": 1209600,  # P14D
        "dnssec_signatures_validity_dnskey": 1209600,  # P14D
        "dnssec_max_zone_ttl": 86400,  # P1D
        "dnssec_zone_propagation_delay": 300,  # PT5M
        "dnssec_parent_ds_ttl": 86400,  # P1D
        "dnssec_parent_propagation_delay": 3600,  # PT1H
        "dnssec_dnskey_ttl": 3600,  # PT1H
    }
    base_url = "netbox-dns"

    def ready(self):
        super().ready()

        import netbox_dns.signals.dnssec  # noqa: F401

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


#
# Initialize plugin config
#
config = DNSConfig
