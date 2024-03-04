# Welcome to NetBox DNS Contribution Guide

Thank you for investing your time in contributing to our project!

## Issues

If you spot a problem with the NetBox DNS, search if an issue already exists. If a related issue doesn't exist, you can open a new one.

Include the following information in your post:

* Use the issue template provided by GitHub when you start a new issue
* Specify your Python, NetBox and NetBox DNS versions. If possible, check if this issue is already fixed in the latest releases or the latest release
* Whenever possible, include a [minimal reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) to help identify the issue
* Describe what actually happened. Include the full traceback if an exception occurred. If possible, set the NetBox Django environment to [DEBUG](https://demo.netbox.dev/static/docs/configuration/optional-settings/#debug) mode to get the full traceback for GUI exceptions, but observe the warning with respect to production systems before doing so

## Submitting Pull Requests

* Please be sure to follow the [NetBox Plugin Development Guide](https://netbox.readthedocs.io/en/stable/plugins/development/), especially with respect to supported interfaces. Exceptions should be rare and be accompanied with a good explanation.
* Make sure to open an issue before starting work on a pull request, and discuss your idea with the NetBox DNS Community before beginning work.
* Create a new branch, ideally with a name like `fix/short-description-of-the-fix` or `feature/short-description-of-the-feature` to make the project history more readable. PRs based on your `main` branch will not be accepted
* All new functionality must include relevant tests if possible
* All code submissions should meet the following criteria, which will be automatically checked by the GitHub CI workflow:
    * Python syntax is valid
    * `black` code formatting is enforced
    * `/opt/netbox/venv/bin/manage.py test netbox_dns' succeeds
* Include a reference to the fixed bug or feature request in the description of the pull request, e.g. `fixes #23`. See the [GitHub documentation](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests) for details
* If the main branch has moved on while you were working on a pull request, please __do not merge but rebase__ your branch. Merging normally isn't required, and it creates merge commits that unnecessarily clutter the project history

## First Time Setup

* Download and install the latest version of `git`
* Configure git with your username and email:

```bash
$ git config --global user.name 'your name'
$ git config --global user.email 'your email'
```

* Fork `netbox-plugin-dns` to your GitHub account by clicking the __Fork__ button.
* Clone the your forked repository locally:

```bash
$ git clone https://github.com/YOUR-GITHUB-USERNAME/netbox-plugin-dns.git
```

* Use the main project's `main` repository as upstream remote:

```bash
$ cd netbox-plugin-dns
$ git remote add upstream https://github.com/peteeckel/netbox-plugin-dns.git
```

* Install NetBox. Please see the [NetBox Installation Guide](https://github.com/netbox-community/netbox/blob/develop/docs/installation/index.md). The following steps assume that you followed that documentation and installed NetBox in `/opt/netbox` and the virtual environment in `/opt/netbox/venv`.
* Activate the NetBox virtual environment (assuming your NetBox installation resides in `/opt/netbox`): 

```bash
$ source /opt/netbox/venv/bin/activate
```

* Install the `black` code formatting utility:

```bash
$ pip3 install black
```

* Install `netbox-plugin-dns`. In a development environment it makes most sense to use an editable installation, which can be achieved by the following commands (assuming you checked out the NetBox DNS repository to `/install-path/netbox-plugin-dns`):

```bash
$ pip3 -e /install-path/netbox-plugin-dns

```

* Add NetBox DNS to the NetBox configuration `/opt/netbox/netbox/netbox/configuration.py`

```python
PLUGINS = [
    "netbox_dns",
]
```

* Restart NetBox

```bash
# systemctl restart netbox netbox-rq
```

After these steps are completed successfully, you're all set up.

## Formatting your code with `black`
To achieve a consistent coding style, all code for the NetBox DNS plugin is formatted using the `black` utility. For more details, see the [documentation](https://black.readthedocs.io/en/stable/index.html) for `black`.

```
$ /opt/netbox/venv/bin/black netbox_dns
```

## Running the Tests

Go to the NetBox directory and run

```bash
$ /opt/netbox/netbox/manage.py test netbox_dns.tests
```
