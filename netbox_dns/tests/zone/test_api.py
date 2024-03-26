from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer


class ZoneTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
    NetBoxDNSGraphQLMixin,
    APIViewTestCases.GraphQLTestCase,
):
    model = Zone

    brief_fields = [
        "active",
        "description",
        "display",
        "id",
        "name",
        "rfc2317_prefix",
        "status",
        "url",
        "view",
    ]

    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial_auto": True,
    }

    @classmethod
    def setUpTestData(cls):
        ns1 = NameServer.objects.create(name="ns1.example.com")

        views = (
            View(name="view1"),
            View(name="view2"),
            View(name="view3"),
        )
        View.objects.bulk_create(views)

        zones = (
            Zone(name="zone1.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(name="zone2.example.com", **cls.zone_data, soa_mname=ns1),
            Zone(
                name="zone3.example.com", **cls.zone_data, soa_mname=ns1, view=views[0]
            ),
            Zone(
                name="zone4.example.com", **cls.zone_data, soa_mname=ns1, view=views[1]
            ),
            Zone(
                name="zone5.example.com", **cls.zone_data, soa_mname=ns1, view=views[2]
            ),
        )
        for zone in zones:
            zone.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "name": "zone6.example.com",
                "status": "reserved",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
            {
                "name": "zone7.example.com",
                "status": "reserved",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
            {
                "name": "zone8.example.com",
                "status": "reserved",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
            {
                "name": "zone9.example.com",
                **cls.zone_data,
                "soa_mname": ns1.pk,
                "view": views[0].pk,
            },
            {
                "name": "zone9.example.com",
                **cls.zone_data,
                "soa_mname": ns1.pk,
                "view": views[1].pk,
            },
            {
                "name": "zone9.example.com",
                **cls.zone_data,
                "soa_mname": ns1.pk,
            },
        ]

        cls.bulk_update_data = {
            "view": views[2].pk,
            "tags": [t.pk for t in tags],
        }
