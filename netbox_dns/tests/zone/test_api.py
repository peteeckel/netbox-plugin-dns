from utilities.testing import APIViewTestCases, create_tags

from netbox_dns.tests.custom import APITestCase, NetBoxDNSGraphQLMixin
from netbox_dns.models import View, Zone, NameServer


class ZoneAPITestCase(
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

    @classmethod
    def setUpTestData(cls):
        nameserver = NameServer.objects.create(name="ns1.example.com")

        zone_data = {
            **Zone.get_defaults(),
            "soa_mname": nameserver,
            "soa_rname": "hostmaster.example.com",
            "soa_serial_auto": False,
        }

        views = (
            View(name="view1"),
            View(name="view2"),
            View(name="view3"),
        )
        View.objects.bulk_create(views)

        zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="zone2.example.com", **zone_data),
            Zone(name="zone3.example.com", **zone_data, view=views[0]),
            Zone(name="zone4.example.com", **zone_data, view=views[1]),
            Zone(name="zone5.example.com", **zone_data, view=views[2]),
        )
        for zone in zones:
            zone.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.create_data = [
            {
                "name": "zone6.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone7.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone8.example.com",
                "status": "reserved",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "view": views[0].pk,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "view": views[1].pk,
                "soa_mname": nameserver.pk,
            },
            {
                "name": "zone9.example.com",
                **zone_data,
                "soa_mname": nameserver.pk,
            },
        ]

        cls.bulk_update_data = {
            "view": views[2].pk,
            "tags": [t.pk for t in tags],
        }
