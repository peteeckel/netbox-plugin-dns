# Welcome to NetBoxDNS Contributing Guide

Thank you for investing your time in contributing to our project!

## Issues

If you spot a problem with the NetBoxDNS, search if an issue already exists. If a related issue doesn't exist, you can open a new one.

Include the following information in your post:

* Describe what you expected to happen.
* If possible, include a [minimal reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) to help us identify the issue.
* Describe what actually happened. Include the full traceback if there was an exception.
* List your Python and NetBox versions. If possible, check if this issue is already fixed in the latest releases or the latest code in the repository.

## Submitting Pull Requests

* Please be sure to check out [NetBox Plugin Development](https://netbox.readthedocs.io/en/stable/plugins/development/) documentation.
* Be sure to open an issue before starting work on a pull request, and discuss your idea with the NetBoxDNS Community before beginning work.
* All new functionality must include relevant tests where applicable.
* When submitting a pull request, please be sure to work off of the `develop` branch, rather than `main`. The `develop` branch is used for ongoing development, while `main` is used for tagging stable releases.
* All code submissions should meet the following criteria (CI will enforce these checks):
    * Python syntax is valid
    * All tests pass when run with `python manage.py test netbox_dns.tests`
    * `black` code formatting compliance is enforced

## First Time Setup

* Download and install the latest version of git.
* Configure git with your username and email.

```
$ git config --global user.name 'your name'
$ git config --global user.email 'your email'
```

* Fork `netbox-plugin-dns` to your GitHub account by clicking the __Fork__ button.
* Clone the your forked repository locally.

```
$ git clone https://github.com/YOUR-GITHUB-USERNAME/netbox-plugin-dns.git
$ cd netbox-plugin-dns
```

* Add main repository as upstream remote.

```
$ git remote add upstream https://github.com/peteeckel/netbox-plugin-dns.git
```

* Install NetBox. Please see [NetBox Installation](https://github.com/netbox-community/netbox#installation)
* Activate NetBox virtual environment: `source netbox/.venv/bin/activate`
* Install `netbox-plugin-dns`

```
$ poetry install
```

Add the plugin to the NetBox config. `~/netbox/configuration.py`

```python
PLUGINS = [
    "netbox_dns",
]
```

* Start coding.

## Running the Tests

Go to the NetBox directory and run

```
$ python manage.py test netbox_dns.tests
```

## Running `black` Code Formatting

```
$ black netbox_dns
```
