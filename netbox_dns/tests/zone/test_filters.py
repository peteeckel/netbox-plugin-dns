from django.test import TestCase

from tenancy.models import Tenant, TenantGroup
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import Zone, ZoneStatusChoices, View, NameServer
from netbox_dns.filters import ZoneFilter


class ZoneFilterTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Zone.objects.all()
    filterset = ZoneFilter

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

        cls.views = (
            View(name="View 1"),
            View(name="View 2"),
        )
        View.objects.bulk_create(cls.views)

        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zones = (
            Zone(
                name="zone1.example.com",
                view=cls.views[0],
                tenant=cls.tenants[0],
                soa_mname=cls.nameservers[0],
                **cls.zone_data
            ),
            Zone(
                name="zone2.example.com",
                view=cls.views[0],
                tenant=cls.tenants[1],
                soa_mname=cls.nameservers[1],
                **cls.zone_data,
                status=ZoneStatusChoices.STATUS_DEPRECATED
            ),
            Zone(
                name="zone3.example.com",
                view=cls.views[0],
                tenant=cls.tenants[2],
                soa_mname=cls.nameservers[2],
                **cls.zone_data
            ),
            Zone(
                name="zone1.example.com",
                view=cls.views[1],
                tenant=cls.tenants[0],
                soa_mname=cls.nameservers[0],
                **cls.zone_data
            ),
            Zone(
                name="zone2.example.com",
                view=cls.views[1],
                tenant=cls.tenants[1],
                soa_mname=cls.nameservers[1],
                **cls.zone_data
            ),
            Zone(
                name="zone3.example.com",
                view=cls.views[1],
                tenant=cls.tenants[2],
                soa_mname=cls.nameservers[2],
                **cls.zone_data
            ),
        )
        Zone.objects.bulk_create(cls.zones)
        for i in range(3):
            cls.zones[i].nameservers.set([cls.nameservers[0].pk, cls.nameservers[1].pk])
        for i in range(3):
            cls.zones[3 + i].nameservers.set(
                [cls.nameservers[1].pk, cls.nameservers[2].pk]
            )

    def test_name(self):
        params = {"name": ["zone1.example.com", "zone2.example.com"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_view(self):
        params = {"view": [self.views[0]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_active(self):
        params = {"active": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_nameservers(self):
        params = {"nameservers": [self.nameservers[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"nameservers": [self.nameservers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"nameservers": [self.nameservers[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_tenant(self):
        params = {"tenant_id": [self.tenants[0].pk, self.tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"tenant": [self.tenants[0].slug, self.tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        params = {
            "tenant_group_id": [self.tenant_groups[0].pk, self.tenant_groups[1].pk]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {
            "tenant_group": [self.tenant_groups[0].slug, self.tenant_groups[1].slug]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
