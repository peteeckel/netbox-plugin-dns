from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import NameServer, View, Zone, ZoneStatusChoices


class ZoneViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Zone

    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_serial": 2021110401,
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial_auto": False,
    }
    zone_value_string = ",".join(str(value) for value in zone_data.values())
    zone_key_string = ",".join(zone_data.keys())

    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

        ns1 = nameservers[0]

        views = (
            View(name="internal"),
            View(name="external"),
        )
        View.objects.bulk_create(views)

        zones = (
            Zone(name="zone1.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(name="zone2.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(name="zone3.example.com", **cls.zone_data, soa_mname=ns1),
        )
        Zone.objects.bulk_create(zones)

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "zone7.example.com",
            "status": ZoneStatusChoices.STATUS_PARKED,
            **cls.zone_data,
            "soa_mname": ns1.pk,
            "tags": [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            "status": ZoneStatusChoices.STATUS_PARKED,
            "default_ttl": 43200,
            "soa_rname": "new-hostmaster.example.com",
            "soa_mname": nameservers[1].pk,
            "nameservers": [nameservers[0].pk, nameservers[2].pk],
            "soa_serial": 2024040101,
            "soa_refresh": 86400,
            "soa_retry": 3600,
            "soa_expire": 256000,
            "soa_ttl": 43200,
            "soa_minimum": 1800,
            "soa_serial_auto": False,
        }

        cls.csv_data = (
            "name,status,soa_mname,soa_rname,nameservers",
            "zone4.example.com,active,ns1.example.com,hostmaster.example.com,",
            "zone5.example.com,active,ns1.example.com,hostmaster.example.com,",
            "zone6.example.com,active,ns1.example.com,hostmaster.example.com,",
            'zone7.example.com,active,ns1.example.com,hostmaster.example.com,"ns2.example.com,ns3.example.com"',
        )

        cls.csv_update_data = (
            "id,status,description,view",
            f"{zones[0].pk},{ZoneStatusChoices.STATUS_PARKED},test-zone1,",
            f"{zones[1].pk},{ZoneStatusChoices.STATUS_ACTIVE},test-zone2,{views[0].name}",
        )
