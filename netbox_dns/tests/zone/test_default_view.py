from django.test import TestCase

from netbox_dns.models import View, NameServer, Zone


class ZoneDefaultViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = View.objects.create(name="test")
        cls.default_view = View.get_default_view()

        cls.zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

    def test_create_zone_explicit_view(self):
        zone = Zone.objects.create(
            name="zone1.example.com", view=self.view, **self.zone_data
        )

        self.view.refresh_from_db()
        self.assertEqual(zone.view, self.view)
        self.assertIn(zone, self.view.zone_set.all())

    def test_create_zone_default_view(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)

        self.default_view.refresh_from_db()
        self.assertEqual(zone.view, self.default_view)
        self.assertIn(zone, self.default_view.zone_set.all())

    def test_modify_zone_default_to_explicit_view(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)

        self.default_view.refresh_from_db()
        self.assertEqual(zone.view, self.default_view)
        self.assertIn(zone, self.default_view.zone_set.all())

        zone.view = self.view
        zone.save()

        self.view.refresh_from_db()
        self.assertEqual(zone.view, self.view)
        self.assertIn(zone, self.view.zone_set.all())

    def test_modify_zone_explicit_to_default_view(self):
        zone = Zone.objects.create(
            name="zone1.example.com", view=self.view, **self.zone_data
        )

        self.view.refresh_from_db()
        self.assertEqual(zone.view, self.view)
        self.assertIn(zone, self.view.zone_set.all())

        zone.view = None
        zone.save()

        self.default_view.refresh_from_db()
        self.assertEqual(zone.view, self.default_view)
        self.assertIn(zone, self.default_view.zone_set.all())
