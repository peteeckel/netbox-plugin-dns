from dns import name as dns_name

__all__ = ("get_parent_zone_names",)


def get_parent_zone_names(name, min_labels=1, include_self=False):
    fqdn = dns_name.from_text(name.lower())
    return [
        fqdn.split(i)[1].to_text().rstrip(".")
        for i in range(min_labels + 1, len(fqdn.labels) + include_self)
    ]
