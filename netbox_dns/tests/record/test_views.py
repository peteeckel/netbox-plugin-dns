from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import (
    View,
    Zone,
    NameServer,
    Record,
    RecordTypeChoices,
    RecordStatusChoices,
)


class RecordViewTestCase(
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
    model = Record

    @classmethod
    def setUpTestData(cls):
        ns1 = NameServer.objects.create(name="ns1.example.com")

        cls.zone_data = {
            "default_ttl": 86400,
            "soa_mname": ns1,
            "soa_rname": "hostmaster.example.com",
            "soa_serial": 2021110401,
            "soa_refresh": 172800,
            "soa_retry": 7200,
            "soa_expire": 2592000,
            "soa_ttl": 86400,
            "soa_minimum": 3600,
            "soa_serial_auto": False,
        }

        cls.views = (
            View(name="view1"),
            View(name="view2"),
        )
        View.objects.bulk_create(cls.views)

        cls.zones = (
            Zone(name="zone1.example.com", **cls.zone_data, view=None),
            Zone(name="zone2.example.com", **cls.zone_data, view=None),
            Zone(name="zone1.example.com", **cls.zone_data, view=cls.views[0]),
            Zone(name="zone2.example.com", **cls.zone_data, view=cls.views[0]),
            Zone(name="zone1.example.com", **cls.zone_data, view=cls.views[1]),
            Zone(name="zone2.example.com", **cls.zone_data, view=cls.views[1]),
        )
        Zone.objects.bulk_create(cls.zones)

        cls.records = (
            Record(
                zone=cls.zones[0],
                type=RecordTypeChoices.CNAME,
                name="name1",
                value="test1.example.com",
                ttl=100,
            ),
            Record(
                zone=cls.zones[1],
                type=RecordTypeChoices.A,
                name="name2",
                value="192.168.1.1",
                ttl=200,
            ),
            Record(
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                name="name2",
                value="fe80:dead:beef::42",
                ttl=86400,
            ),
            Record(
                zone=cls.zones[4],
                type=RecordTypeChoices.TXT,
                name="@",
                value="Test Text",
                ttl=86400,
            ),
        )
        for record in cls.records:
            record.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "zone": cls.zones[0].pk,
            "type": RecordTypeChoices.AAAA,
            "name": "name3",
            "value": "fe80::dead:beef",
            "ttl": 86230,
            "tags": [t.pk for t in tags],
            "status": "active",
        }

        cls.bulk_edit_data = {
            "zone": cls.zones[1].pk,
            "type": RecordTypeChoices.TXT,
            "value": "Test",
            "status": RecordStatusChoices.STATUS_INACTIVE,
            "ttl": 86420,
            "disable_ptr": True,
            "description": "New Description",
        }

        cls.csv_data = (
            "zone,view,type,name,value,ttl",
            "zone1.example.com,,A,@,10.10.10.10,3600",
            "zone2.example.com,,AAAA,name4,fe80::dead:beef,7200",
            "zone1.example.com,,CNAME,dns,name1.zone2.example.com,100",
            "zone2.example.com,,TXT,textname,textvalue,1000",
            "zone1.example.com,view1,A,@,10.10.10.10,3600",
            "zone2.example.com,view1,AAAA,name4,fe80::dead:beef,7200",
            "zone1.example.com,view1,CNAME,dns,name1.zone2.example.com,100",
            "zone2.example.com,view1,TXT,textname,textvalue,1000",
            "zone1.example.com,view2,A,@,10.10.10.10,3600",
            "zone2.example.com,view2,AAAA,name4,fe80::dead:beef,7200",
            "zone1.example.com,view2,CNAME,dns,name1.zone2.example.com,100",
            "zone2.example.com,view2,TXT,textname,textvalue,1000",
        )

        cls.csv_update_data = (
            "id,zone,type,value,ttl",
            f"{cls.records[0].pk},{cls.zones[0].name},{RecordTypeChoices.A},10.0.1.1,86442",
            f"{cls.records[1].pk},{cls.zones[1].name},{RecordTypeChoices.AAAA},fe80:dead:beef::23,86423",
        )

    maxDiff = None
