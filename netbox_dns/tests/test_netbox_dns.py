from django.urls import reverse
from django.test import SimpleTestCase

from netbox_dns import __version__
from netbox_dns.tests.custom import APITestCase


class NetBoxDNSVersionTestCase(SimpleTestCase):
    def test_version(self):
        assert __version__ == "1.0.6"


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_dns-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)
