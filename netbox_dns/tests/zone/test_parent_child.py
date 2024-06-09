from dns import rdata

from django.test import TestCase

from netbox_dns.models import View, NameServer, Zone


class ZoneParentChildTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = View.objects.create(name="test")

        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

    def test_child_zones_same_view(self):
        zones = (
            Zone(name="zone1.example.com", **self.zone_data),
            Zone(name="sub1.zone1.example.com", **self.zone_data),
            Zone(name="sub2.zone1.example.com", **self.zone_data),
            Zone(name="sub3.zone1.example.com", **self.zone_data),
        )
        for zone in zones:
            zone.save()

        for child_zone in zones[1:]:
            self.assertIn(child_zone, zones[0].child_zones)
            self.assertEqual(child_zone.parent_zone, zones[0])

    def test_child_zones_different_view(self):
        zones = (
            Zone(name="zone1.example.com", **self.zone_data),
            Zone(name="sub1.zone1.example.com", **self.zone_data, view=self.view),
            Zone(name="sub2.zone1.example.com", **self.zone_data, view=self.view),
            Zone(name="sub3.zone1.example.com", **self.zone_data, view=self.view),
        )
        for zone in zones:
            zone.save()

        for child_zone in zones[1:]:
            self.assertNotIn(child_zone, zones[0].child_zones)
            self.assertEqual(child_zone.parent_zone, None)

    def test_indirect_child_zones_same_view(self):
        zones = (
            Zone(name="zone1.example.com", **self.zone_data),
            Zone(name="subsub.sub1.zone1.example.com", **self.zone_data),
            Zone(name="subsub.sub2.zone1.example.com", **self.zone_data),
            Zone(name="subsub.sub3.zone1.example.com", **self.zone_data),
        )
        for zone in zones:
            zone.save()

        for child_zone in zones[1:]:
            self.assertNotIn(child_zone, zones[0].child_zones)
            self.assertEqual(child_zone.parent_zone, None)
