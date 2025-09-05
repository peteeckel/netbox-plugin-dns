from ipam.models import Prefix
from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import View, NameServer, Zone


class ViewViewTestCase(
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
    model = View

    def _get_queryset(self):
        return self.model.objects.filter(default_view=False)

    @classmethod
    def setUpTestData(cls):
        cls.views = [
            View(name="external"),
            View(name="internal"),
        ]
        View.objects.bulk_create(cls.views)

        prefixes = (
            Prefix(prefix="10.13.1.0/24"),
            Prefix(prefix="10.23.1.0/24"),
            Prefix(prefix="10.37.1.0/24"),
            Prefix(prefix="10.42.1.0/24"),
        )
        Prefix.objects.bulk_create(prefixes)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "test1",
            "description": "Test View 1",
            "prefixes": [prefix.pk for prefix in prefixes],
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "description": "New Description",
        }

        cls.csv_data = (
            "name,prefixes",
            "test2,",
            "test3,",
            f'test4,"{prefixes[0].id},{prefixes[1].id}"',
        )

        cls.csv_update_data = (
            "id,name,description,prefixes",
            f"{cls.views[0].pk},new-internal,test1,",
            f'{cls.views[1].pk},new-external,test2,"{prefixes[1].id},{prefixes[2].id}"',
        )

    maxDiff = None

    def test_zones_viewtab(self):
        view = self.views[0]

        nameserver = NameServer.objects.create(name="ns1.example.com")
        Zone.objects.create(
            view=view,
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        self.add_permissions(
            "netbox_dns.view_view",
        )

        request = {
            "path": self._get_url("zones", instance=view),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)
