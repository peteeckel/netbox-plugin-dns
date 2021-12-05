from django.urls import reverse
from utilities.testing import APIViewTestCases

from netbox_dns.core.test import APITestCase
from netbox_dns.models import NameServer, Record, Zone


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("plugins-api:netbox_dns-api:api-root")
        response = self.client.get("{}?format=api".format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ZoneTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = Zone
    brief_fields = [
        "created",
        "custom_field_data",
        "default_ttl",
        "display",
        "id",
        "last_updated",
        "name",
        "nameservers",
        "soa_expire",
        "soa_minimum",
        "soa_mname",
        "soa_refresh",
        "soa_retry",
        "soa_rname",
        "soa_serial",
        "soa_serial_auto",
        "soa_ttl",
        "status",
        "tags",
        "url",
    ]

    bulk_update_data = {
        "status": "active",
    }

    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial_auto": False,
    }

    @classmethod
    def setUpTestData(cls):
        ns1 = NameServer.objects.create(name="ns1.example.com")

        zones = (
            Zone(name="zone1.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(name="zone2.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(name="zone3.example.com", **cls.zone_data, soa_mname=ns1),
        )
        Zone.objects.bulk_create(zones)

        cls.create_data = [
            {
                "name": "zone4.example.com",
                "status": "passive",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
            {
                "name": "zone5.example.com",
                "status": "passive",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
            {
                "name": "zone6.example.com",
                "status": "passive",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
        ]


class NameServerTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NameServer
    brief_fields = ["display", "id", "name", "url"]
    create_data = [
        {"name": "ns1.example.com"},
        {"name": "ns2.example.com"},
        {"name": "ns3.example.com"},
    ]

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns4.example.com"),
            NameServer(name="ns5.example.com"),
            NameServer(name="ns6.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)


class RecordTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = Record
    brief_fields = ["display", "id", "name", "ttl", "type", "url", "value"]
    bulk_update_data = {
        "ttl": 19200,
    }

    @classmethod
    def setUpTestData(cls):
        ns1 = NameServer.objects.create(name="ns1.example.com")

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

        zones = (
            Zone(name="zone1.example.com", **zone_data, soa_mname=ns1),
            Zone(name="zone2.example.com", **zone_data, soa_mname=ns1),
            Zone(name="zone3.example.com", **zone_data, soa_mname=ns1),
        )
        Zone.objects.bulk_create(zones)

        records = (
            Record(
                zone=zones[0],
                type=Record.A,
                name="example1",
                value="192.168.1.1",
                ttl=5000,
            ),
            Record(
                zone=zones[1],
                type=Record.AAAA,
                name="example2",
                value="fe80::dead:beef",
                ttl=6000,
            ),
            Record(
                zone=zones[2],
                type=Record.TXT,
                name="example3",
                value="TXT Record",
                ttl=7000,
            ),
        )
        Record.objects.bulk_create(records)

        cls.create_data = [
            {
                "zone": zones[0].pk,
                "type": Record.A,
                "name": "example4",
                "value": "1.1.1.1",
                "ttl": 9600,
            },
            {
                "zone": zones[1].pk,
                "type": Record.AAAA,
                "name": "example5",
                "value": "fe80::dead:beef",
                "disable_ptr": True,
                "ttl": 9600,
            },
            {
                "zone": zones[2].pk,
                "type": Record.TXT,
                "name": "example6",
                "value": "TXT Record",
                "ttl": 9600,
            },
        ]
