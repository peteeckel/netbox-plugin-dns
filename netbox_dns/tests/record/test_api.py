from utilities.testing import APIViewTestCases

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer, Record, RecordTypeChoices


class RecordAPITestCase(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = Record
    brief_fields = [
        "active",
        "description",
        "display",
        "fqdn",
        "id",
        "name",
        "status",
        "ttl",
        "type",
        "url",
        "value",
        "zone",
    ]
    bulk_update_data = {
        "ttl": 19200,
    }

    @classmethod
    def setUpTestData(cls):
        zone_data = {
            **Zone.get_defaults(),
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
            "soa_serial_auto": False,
        }

        views = (
            View(name="view1"),
            View(name="view2"),
        )
        View.objects.bulk_create(views)

        default_view = View.get_default_view()
        zones = (
            Zone(name="zone1.example.com", **zone_data, view=default_view),
            Zone(name="zone2.example.com", **zone_data, view=default_view),
            Zone(name="zone3.example.com", **zone_data, view=default_view),
            Zone(name="zone1.example.com", **zone_data, view=views[0]),
            Zone(name="zone2.example.com", **zone_data, view=views[0]),
            Zone(name="zone3.example.com", **zone_data, view=views[0]),
            Zone(name="zone1.example.com", **zone_data, view=views[1]),
            Zone(name="zone2.example.com", **zone_data, view=views[1]),
            Zone(name="zone3.example.com", **zone_data, view=views[1]),
        )
        Zone.objects.bulk_create(zones)

        records = (
            Record(
                zone=zones[0],
                type=RecordTypeChoices.A,
                name="example1",
                value="192.168.1.1",
                ttl=5000,
            ),
            Record(
                zone=zones[1],
                type=RecordTypeChoices.AAAA,
                name="example2",
                value="fe80::dead:beef",
                ttl=6000,
            ),
            Record(
                zone=zones[2],
                type=RecordTypeChoices.TXT,
                name="example3",
                value="TXT Record",
                ttl=7000,
            ),
            Record(
                zone=zones[3],
                type=RecordTypeChoices.A,
                name="example1",
                value="192.168.1.1",
                ttl=5000,
            ),
            Record(
                zone=zones[4],
                type=RecordTypeChoices.AAAA,
                name="example2",
                value="fe80::dead:beef",
                ttl=6000,
            ),
            Record(
                zone=zones[5],
                type=RecordTypeChoices.TXT,
                name="example3",
                value="TXT Record",
                ttl=7000,
            ),
            Record(
                zone=zones[6],
                type=RecordTypeChoices.A,
                name="example1",
                value="192.168.1.1",
                ttl=5000,
            ),
            Record(
                zone=zones[7],
                type=RecordTypeChoices.AAAA,
                name="example2",
                value="fe80::dead:beef",
                ttl=6000,
            ),
            Record(
                zone=zones[8],
                type=RecordTypeChoices.TXT,
                name="example3",
                value="TXT Record",
                ttl=7000,
            ),
        )
        for record in records:
            record.save()

        cls.create_data = [
            {
                "zone": zones[0].pk,
                "type": RecordTypeChoices.A,
                "name": "example4",
                "value": "1.1.1.1",
                "ttl": 9600,
            },
            {
                "zone": zones[1].pk,
                "type": RecordTypeChoices.AAAA,
                "name": "example5",
                "value": "fe80::dead:beef",
                "disable_ptr": True,
                "ttl": 9600,
            },
            {
                "zone": zones[2].pk,
                "type": RecordTypeChoices.TXT,
                "name": "example6",
                "value": "TXT Record",
                "ttl": 9600,
            },
            {
                "zone": zones[3].pk,
                "type": RecordTypeChoices.A,
                "name": "example4",
                "value": "1.1.1.1",
                "ttl": 9600,
            },
            {
                "zone": zones[4].pk,
                "type": RecordTypeChoices.AAAA,
                "name": "example5",
                "value": "fe80::dead:beef",
                "disable_ptr": True,
                "ttl": 9600,
            },
            {
                "zone": zones[5].pk,
                "type": RecordTypeChoices.TXT,
                "name": "example6",
                "value": "TXT Record",
                "ttl": 9600,
            },
            {
                "zone": zones[6].pk,
                "type": RecordTypeChoices.A,
                "name": "example4",
                "value": "1.1.1.1",
                "ttl": 9600,
            },
            {
                "zone": zones[7].pk,
                "type": RecordTypeChoices.AAAA,
                "name": "example5",
                "value": "fe80::dead:beef",
                "disable_ptr": True,
                "ttl": 9600,
            },
            {
                "zone": zones[8].pk,
                "type": RecordTypeChoices.TXT,
                "name": "example6",
                "value": "TXT Record",
                "ttl": 9600,
            },
        ]
