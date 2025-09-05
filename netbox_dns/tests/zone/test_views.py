from datetime import date

from utilities.testing import ViewTestCases, create_tags

from netbox_dns.tests.custom import ModelViewTestCase
from netbox_dns.models import NameServer, View, Zone, Record, Registrar
from netbox_dns.choices import (
    ZoneStatusChoices,
    ZoneEPPStatusChoices,
    RecordTypeChoices,
)


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

    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(nameservers)

        cls.registrar = Registrar.objects.create(name="Test Registrar")

        cls.zone_data = {
            **Zone.get_defaults(),
            "soa_mname": nameservers[0],
            "soa_rname": "hostmaster.example.com",
            "soa_serial_auto": False,
        }

        views = (
            View(name="internal"),
            View(name="external"),
        )
        View.objects.bulk_create(views)

        default_view = View.get_default_view()
        cls.zones = (
            Zone(name="zone1.example.com", **cls.zone_data),
            Zone(name="zone2.example.com", **cls.zone_data),
            Zone(name="zone3.example.com", **cls.zone_data),
        )
        for zone in cls.zones:
            zone.save()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "zone7.example.com",
            "status": ZoneStatusChoices.STATUS_PARKED,
            **cls.zone_data,
            "view": default_view.pk,
            "soa_mname": nameservers[0].pk,
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
            "registrar": cls.registrar.pk,
            "expiration_date": date(2025, 4, 1),
            "domain_status": ZoneEPPStatusChoices.EPP_STATUS_CLIENT_TRANSFER_PROHIBITED,
        }

        cls.csv_data = (
            "name,status,soa_mname,soa_rname,nameservers,domain_status",
            "zone4.example.com,active,ns1.example.com,hostmaster.example.com,,",
            "zone5.example.com,active,ns1.example.com,hostmaster.example.com,,",
            "zone6.example.com,active,ns1.example.com,hostmaster.example.com,,",
            f'zone7.example.com,active,ns1.example.com,hostmaster.example.com,"ns2.example.com,ns3.example.com",{ZoneEPPStatusChoices.EPP_STATUS_CLIENT_TRANSFER_PROHIBITED}',
        )

        cls.csv_update_data = (
            "id,status,description,view,nameservers,domain_status",
            f"{cls.zones[0].pk},{ZoneStatusChoices.STATUS_PARKED},test-zone1,,{nameservers[1].name},{ZoneEPPStatusChoices.EPP_STATUS_OK}",
            f'{cls.zones[1].pk},{ZoneStatusChoices.STATUS_ACTIVE},test-zone2,{views[0].name},"{nameservers[1].name},{nameservers[2].name}",',
        )

    def test_records_viewtab(self):
        zone = self.zones[0]

        Record.objects.create(
            name="test",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::42",
        )

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("records", instance=zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_registration_viewtab(self):
        zone = self.zones[0]
        zone.registrar = self.registrar
        zone.save()

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("registration", instance=zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_managed_records_viewtab(self):
        zone = self.zones[0]

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("managed_records", instance=zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_delegation_records_viewtab(self):
        zone = self.zones[0]

        Zone.objects.create(name=f"sub.{zone.name}", **self.zone_data)
        Record.objects.create(
            name="sub",
            zone=zone,
            type=RecordTypeChoices.NS,
            value=f"ns1.sub.{zone.name}",
        )

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("delegation_records", instance=zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_parent_delegation_records_viewtab(self):
        zone = self.zones[0]

        child_zone = Zone.objects.create(name=f"sub.{zone.name}", **self.zone_data)
        Record.objects.create(
            name="sub",
            zone=zone,
            type=RecordTypeChoices.NS,
            value=f"ns1.sub.{zone.name}",
        )

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("parent_delegation_records", instance=child_zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_rfc2317_child_zones_viewtab(self):
        zone = Zone.objects.create(name="0.168.192.in-addr.arpa", **self.zone_data)
        Zone.objects.create(
            name="0-15.0.168.192.in-addr.arpa",
            **self.zone_data,
            rfc2317_prefix="192.168.0.0/28",
            rfc2317_parent_managed=True,
        )

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("rfc2317_child_zones", instance=zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)

    def test_child_zones_viewtab(self):
        zone = self.zones[0]

        child_zone = Zone.objects.create(name=f"sub.{zone.name}", **self.zone_data)

        self.add_permissions(
            "netbox_dns.view_zone",
        )

        request = {
            "path": self._get_url("child_zones", instance=child_zone),
        }

        response = self.client.get(**request)
        self.assertHttpStatus(response, 200)
