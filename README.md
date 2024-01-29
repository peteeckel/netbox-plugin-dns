# NetBox DNS
The NetBox DNS plugin enables NetBox to manage operational DNS data such as name servers, zones, records and views, as well as registration data for domains. It can automate tasks like creating PTR records, generating zone serial numbers, NS and SOA records, as well as validate names and values values for resource records to ensure zone data is consistent, current and conforming to the relevant RFCs.

<div align="center">
<a href="https://pypi.org/project/netbox-plugin-dns/"><img src="https://img.shields.io/pypi/v/netbox-plugin-dns" alt="PyPi"/></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/stargazers"><img src="https://img.shields.io/github/stars/peteeckel/netbox-plugin-dns?style=flat" alt="Stars Badge"/></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/network/members"><img src="https://img.shields.io/github/forks/peteeckel/netbox-plugin-dns?style=flat" alt="Forks Badge"/></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/issues"><img src="https://img.shields.io/github/issues/peteeckel/netbox-plugin-dns" alt="Issues Badge"/></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/pulls"><img src="https://img.shields.io/github/issues-pr/peteeckel/netbox-plugin-dns" alt="Pull Requests Badge"/></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/peteeckel/netbox-plugin-dns?color=2b9348"></a>
<a href="https://github.com/peteeckel/netbox-plugin-dns/blob/master/LICENSE"><img src="https://img.shields.io/github/license/peteeckel/netbox-plugin-dns?color=2b9348" alt="License Badge"/></a>
<a href="https://pepy.tech/project/netbox-plugin-dns"><img alt="Downloads" src="https://static.pepy.tech/badge/netbox-plugin-dns"></a>
<a href="https://pepy.tech/project/netbox-plugin-dns"><img alt="Downloads/Week" src="https://static.pepy.tech/badge/netbox-plugin-dns/month"></a>
<a href="https://pepy.tech/project/netbox-plugin-dns"><img alt="Downloads/Month" src="https://static.pepy.tech/badge/netbox-plugin-dns/week"></a>
</div>

## Features

* Manage name servers, zones and records
* Automatically generate SOA and NS records for zones
* Automatically create and update PTR records for IPv4 and IPv6 address records
* Organize DNS zones in views for split horizon DNS and multi-site deployments
* Manage domain registrar and registrant information for domains related to zones
* Manage RFC2317 reverse zones for IPv4 prefixes with a network mask length longer than 24 bits

NetBox DNS is using the standardized NetBox plugin interface, so it also takes advantage of the NetBox tagging and change log features.

## Requirements

* NetBox 4.0.0 or higher
* Python 3.10 or higher

## Installation & Configuration

### Installation

```
$ source /opt/netbox/venv/bin/activate
(venv) $ pip install netbox-plugin-dns
```

### NetBox Configuration

Add the plugin to the NetBox config. `~/netbox/configuration.py`

```python
PLUGINS = [
    "netbox_dns",
]
```

To permanently keep the plugin installed when updating NetBox via `update.sh`:

```
echo netbox-plugin-dns >> ~/netbox/local_requirements.txt
```

To add the required netbox_dns tables to your database run the following command from your NetBox directory:

```
./manage.py migrate
```

Full documentation on using plugins with NetBox: [Using Plugins - NetBox Documentation](https://netbox.readthedocs.io/en/stable/plugins/)

## Contribute

Contributions are always welcome! Please see: [contributing guide](CONTRIBUTING.md)

## Documentation

For further information, please refer to the full documentation: [Using NetBox DNS](docs/using_netbox_dns.md)

## License

MIT
