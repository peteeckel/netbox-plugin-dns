from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import NameServer, Zone


class NameServerViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = NameServer

    @classmethod
    def setUpTestData(cls):
        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "ns4.example.com",
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "New Description",
        }

        cls.csv_data = (
            "name",
            "ns5.example.com",
            "ns6.example.com",
            "ns7.example.com",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{cls.nameservers[0].pk},ns8.example.com,test1",
            f"{cls.nameservers[1].pk},ns9.example.com,test2",
            f"{cls.nameservers[2].pk},ns10.example.com,test3",
        )

    maxDiff = None

    def test_zones_viewtab(self):
        soa_nameserver = self.nameservers[0]
        nameserver = self.nameservers[1]

        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=soa_nameserver,
            soa_rname="hostmaster.example.com",
        )
        zone.nameservers.set([nameserver])

        self.add_permissions(
            "netbox_dns.view_nameserver",
        )

        request = {
            "path": self._get_url("zones", instance=nameserver),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_soa_zones_viewtab(self):
        soa_nameserver = self.nameservers[0]

        Zone.objects.create(
            name="zone1.example.com",
            soa_mname=soa_nameserver,
            soa_rname="hostmaster.example.com",
        )

        self.add_permissions(
            "netbox_dns.view_nameserver",
        )

        request = {
            "path": self._get_url("soa_zones", instance=soa_nameserver),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)
