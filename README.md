<h1 align="center">NetBox DNS</h1>

<p align="center"><i>NetBox DNS is a NetBox plugin for managing DNS views, zones, name servers and records.</i></p>

<div align="center">
<a href="https://pypi.org/project/netbox-dns/"><img src="https://img.shields.io/pypi/v/netbox-dns" alt="PyPi"/></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/stargazers"><img src="https://img.shields.io/github/stars/auroraresearchlab/netbox-dns" alt="Stars Badge"/></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/network/members"><img src="https://img.shields.io/github/forks/auroraresearchlab/netbox-dns" alt="Forks Badge"/></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/pulls"><img src="https://img.shields.io/github/issues-pr/auroraresearchlab/netbox-dns" alt="Pull Requests Badge"/></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/issues"><img src="https://img.shields.io/github/issues/auroraresearchlab/netbox-dns" alt="Issues Badge"/></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/auroraresearchlab/netbox-dns?color=2b9348"></a>
<a href="https://github.com/auroraresearchlab/netbox-dns/blob/master/LICENSE"><img src="https://img.shields.io/github/license/auroraresearchlab/netbox-dns?color=2b9348" alt="License Badge"/></a>
</div>

## Features

* Manage DNS name servers
* Manage DNS zone information, automatically generating SOA and NS records
* Manage DNS records
* Automatically create and update PTR records for A and AAAA records
* Optionally organize DNS zones in views to cater for split horizon DNS and multi-site deployments

NetBox DNS is using the standardized NetBox plugin interface, so it also takes advantage of the NetBox tagging and change log features.

## Requirements

* NetBox 3.5 or higher
* Python 3.8 or higher

## Installation & Configuration

### Installation

```
$ source /opt/netbox/venv/bin/activate
(venv) $ pip install netbox-dns
```

### Configuration

Add the plugin to the NetBox config. `~/netbox/configuration.py`

```python
PLUGINS = [
    "netbox_dns",
]
```

To permanently mount the plugin when updating NetBox:

```
echo netbox-dns >> ~/netbox/local_requirements.txt
```

To add the required netbox_dns tables to your database run the following command from your NetBox directory:

```
./manage.py migrate
```

Full reference: [Using Plugins - NetBox Documentation](https://netbox.readthedocs.io/en/stable/plugins/)

## Screenshots

![Zones](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/ZoneList.png)

![Zone Detail](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/ZoneDetail.png)

![Records](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/RecordList.png)

![Record Detail](https://raw.githubusercontent.com/auroraresearchlab/netbox-dns/main/docs/images/RecordDetail.png)

## Contribute

Contributions are always welcome! Please see: [contributing guide](CONTRIBUTING.md)

## License

MIT
