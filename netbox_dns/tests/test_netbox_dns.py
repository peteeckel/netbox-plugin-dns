from django.test import SimpleTestCase

from netbox_dns import __version__


class NetboxDnsTestCase(SimpleTestCase):
    """
    Test for netbox_dns package
    """

    def test_version(self):
        assert __version__ == "0.6.3"
