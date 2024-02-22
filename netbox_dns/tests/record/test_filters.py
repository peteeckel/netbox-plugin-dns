from django.test import TestCase

from tenancy.models import Tenant, TenantGroup
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import (
    Zone,
    ZoneStatusChoices,
    NameServer,
    Record,
    RecordTypeChoices,
)
from netbox_dns.filtersets import RecordFilterSet


class RecordFilterTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Record.objects.all()
    filterset = RecordFilterSet

    zone_data = {
        "default_ttl": 86400,
        "soa_rname": "hostmaster.example.com",
        "soa_refresh": 172800,
        "soa_retry": 7200,
        "soa_expire": 2592000,
        "soa_ttl": 86400,
        "soa_minimum": 3600,
        "soa_serial": 1,
        "soa_serial_auto": False,
    }

    @classmethod
    def setUpTestData(cls):
        cls.tenant_groups = (
            TenantGroup(name="Tenant group 1", slug="tenant-group-1"),
            TenantGroup(name="Tenant group 2", slug="tenant-group-2"),
            TenantGroup(name="Tenant group 3", slug="tenant-group-3"),
        )
        for tenantgroup in cls.tenant_groups:
            tenantgroup.save()

        cls.tenants = (
            Tenant(name="Tenant 1", slug="tenant-1", group=cls.tenant_groups[0]),
            Tenant(name="Tenant 2", slug="tenant-2", group=cls.tenant_groups[1]),
            Tenant(name="Tenant 3", slug="tenant-3", group=cls.tenant_groups[2]),
        )
        Tenant.objects.bulk_create(cls.tenants)

        cls.nameservers = (NameServer(name="ns1.example.com"),)
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zones = (
            Zone(
                name="zone1.example.com", soa_mname=cls.nameservers[0], **cls.zone_data
            ),
            Zone(
                name="zone2.example.com",
                soa_mname=cls.nameservers[0],
                **cls.zone_data,
                status=ZoneStatusChoices.STATUS_DEPRECATED
            ),
        )
        Zone.objects.bulk_create(cls.zones)

        cls.records = (
            Record(
                name="name1",
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                value="fe80::dead:beef",
                tenant=cls.tenants[0],
            ),
            Record(
                name="name2",
                zone=cls.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.42",
                tenant=cls.tenants[0],
            ),
            Record(
                name="name3",
                zone=cls.zones[0],
                type=RecordTypeChoices.AAAA,
                value="fe80::dead:beef",
                tenant=cls.tenants[1],
                managed=True,
            ),
            Record(
                name="name1",
                zone=cls.zones[1],
                type=RecordTypeChoices.AAAA,
                value="fe80::dead:beef",
                tenant=cls.tenants[0],
            ),
            Record(
                name="name2",
                zone=cls.zones[1],
                type=RecordTypeChoices.A,
                value="10.0.0.42",
                tenant=cls.tenants[0],
            ),
            Record(
                name="name3",
                zone=cls.zones[1],
                type=RecordTypeChoices.AAAA,
                value="fe80::dead:beef",
                tenant=cls.tenants[1],
                managed=True,
            ),
        )
        for record in cls.records:
            record.save()

    def test_name(self):
        params = {"name": ["name1", "name2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_zone(self):
        params = {"zone": [self.zones[0]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_fqdn(self):
        params = {
            "fqdn": [
                "name1.zone1.example.com",
                "name2.zone1.example.com",
                "name4.zone1.example.com",
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "fqdn": [
                "name1.zone2.example.com.",
                "name2.zone2.example.com.",
                "name2.zone1.example",
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {"type": [RecordTypeChoices.A]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"type": [RecordTypeChoices.AAAA]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_value(self):
        params = {"value": ["10.0.0.42"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"value": ["fe80::dead:beef"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"value": ["fe80::dead:beef", "10.0.0.42"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_managed(self):
        params = {"managed": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"managed": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        params = {"tenant_id": [self.tenants[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"tenant": [self.tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        params = {"tenant_group_id": [self.tenant_groups[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"tenant_group": [self.tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
