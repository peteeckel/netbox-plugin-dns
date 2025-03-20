import re

from dns import name as dns_name
from dns.exception import DNSException
from netaddr import IPNetwork, AddrFormatError

from django.utils.dateparse import parse_duration

from netbox.plugins.utils import get_plugin_config


__all__ = (
    "NameFormatError",
    "arpa_to_prefix",
    "name_to_unicode",
    "value_to_unicode",
    "normalize_name",
    "network_to_reverse",
    "regex_from_list",
    "iso8601_to_int",
)


class NameFormatError(Exception):
    pass


def arpa_to_prefix(arpa_name):
    name = arpa_name.rstrip(".")

    if name.endswith(".in-addr.arpa"):
        address = ".".join(reversed(name.replace(".in-addr.arpa", "").split(".")))
        mask = len(address.split(".")) * 8
        address = address + (32 - mask) // 8 * ".0"

        try:
            return IPNetwork(f"{address}/{mask}")
        except (AddrFormatError, ValueError):
            return None

    elif name.endswith("ip6.arpa"):
        address = "".join(reversed(name.replace(".ip6.arpa", "").split(".")))
        mask = len(address)
        address = address + "0" * (32 - mask)

        try:
            return IPNetwork(
                f"{':'.join([(address[i:i+4]) for i in range(0, 32, 4)])}/{mask*4}"
            )
        except AddrFormatError:
            return None

    else:
        return None


def name_to_unicode(name):
    if name == "." and get_plugin_config("netbox_dns", "enable_root_zones"):
        return "."

    try:
        return dns_name.from_text(name, origin=None).to_unicode()
    except dns_name.IDNAException:
        return name


def value_to_unicode(value):
    return re.sub(
        r"xn--[0-9a-z-_.]*",
        lambda x: name_to_unicode(x.group(0)),
        value,
        flags=re.IGNORECASE,
    )


def normalize_name(name):
    if name == "." and get_plugin_config("netbox_dns", "enable_root_zones"):
        return "."

    try:
        return (
            dns_name.from_text(name, origin=dns_name.root)
            .relativize(dns_name.root)
            .to_text()
        )

    except DNSException as exc:
        raise NameFormatError from exc


def network_to_reverse(network):
    try:
        ip_network = IPNetwork(network)
    except AddrFormatError:
        return

    if ip_network.first == ip_network.last:
        return

    labels = None
    match ip_network.version:
        case 4:
            if not ip_network.prefixlen % 8:
                labels = 3 + ip_network.prefixlen // 8
        case 6:
            if not ip_network.prefixlen % 4:
                labels = 3 + ip_network.prefixlen // 4
        case _:
            return

    if labels:
        return ".".join(ip_network[0].reverse_dns.split(".")[-labels:])


def regex_from_list(names):
    return f"^({'|'.join(re.escape(name) for name in names)})$"


def iso8601_to_int(value):
    try:
        return int(value)
    except ValueError:
        duration = parse_duration(value)
        if duration is None:
            raise TypeError
        return int(duration.total_seconds())
