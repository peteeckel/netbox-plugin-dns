from django.test import TestCase

from tenancy.models import Tenant, TenantGroup
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_dns.models import (
    Zone,
    ZoneStatusChoices,
    View,
    NameServer,
    Registrar,
    Contact,
)
from netbox_dns.filtersets import ZoneFilterSet


class ZoneFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Zone.objects.all()
    filterset = ZoneFilterSet

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

        cls.registrars = (
            Registrar(name="ACME 2 Corporation", iana_id=4242),
            Registrar(name="ACME 2 Limited", iana_id=2323),
            Registrar(name="ACME 2 Trust", iana_id=55),
        )
        Registrar.objects.bulk_create(cls.registrars)

        cls.contacts = (
            Contact(name="Paul Example", contact_id="4242"),
            Contact(name="Fred Example", contact_id="2323"),
            Contact(name="Jack Example", contact_id="0815"),
        )
        Contact.objects.bulk_create(cls.contacts)

        cls.zones = (
            Zone(
                name="zone1.example.com",
                view=cls.views[0],
                tenant=cls.tenants[0],
                soa_mname=cls.nameservers[0],
                registry_domain_id="acme-001-4242",
                registrar=cls.registrars[0],
                registrant=cls.contacts[0],
                tech_c=cls.contacts[0],
                admin_c=cls.contacts[0],
                billing_c=cls.contacts[0],
                **cls.zone_data,
            ),
            Zone(
                name="zone2.example.com",
                view=cls.views[0],
                tenant=cls.tenants[1],
                soa_mname=cls.nameservers[1],
                status=ZoneStatusChoices.STATUS_DEPRECATED,
                registry_domain_id="acme-001-2323",
                registrar=cls.registrars[1],
                registrant=cls.contacts[1],
                tech_c=cls.contacts[1],
                admin_c=cls.contacts[1],
                billing_c=cls.contacts[1],
                **cls.zone_data,
            ),
            Zone(
                name="zone3.example.com",
                view=cls.views[0],
                tenant=cls.tenants[2],
                soa_mname=cls.nameservers[2],
                registry_domain_id="acme-002-2323",
                registrar=cls.registrars[1],
                registrant=cls.contacts[1],
                tech_c=cls.contacts[1],
                admin_c=cls.contacts[1],
                billing_c=cls.contacts[1],
                **cls.zone_data,
            ),
            Zone(
                name="zone1.example.com",
                view=cls.views[1],
                tenant=cls.tenants[0],
                soa_mname=cls.nameservers[0],
                registry_domain_id="acme-002-4242",
                registrar=cls.registrars[1],
                registrant=cls.contacts[1],
                tech_c=cls.contacts[1],
                admin_c=cls.contacts[1],
                billing_c=cls.contacts[1],
                **cls.zone_data,
            ),
            Zone(
                name="zone2.example.com",
                view=cls.views[1],
                tenant=cls.tenants[1],
                soa_mname=cls.nameservers[1],
                registry_domain_id="acme-003-4223",
                registrar=cls.registrars[2],
                registrant=cls.contacts[2],
                tech_c=cls.contacts[2],
                admin_c=cls.contacts[2],
                billing_c=cls.contacts[2],
                **cls.zone_data,
            ),
            Zone(
                name="zone3.example.com",
                view=cls.views[1],
                tenant=cls.tenants[2],
                soa_mname=cls.nameservers[2],
                registry_domain_id="acme-003-2342",
                registrar=cls.registrars[0],
                registrant=cls.contacts[2],
                tech_c=cls.contacts[2],
                admin_c=cls.contacts[2],
                billing_c=cls.contacts[2],
                **cls.zone_data,
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

    def test_registrar(self):
        params = {"registrar": [self.registrars[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"registrar": [self.registrars[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_registry_domain_id(self):
        params = {
            "registry_domain_id": ["acme-002-2323", "acme-003-4223", "acme-002-7654"]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_registrant(self):
        params = {"registrant": [self.contacts[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_admin_c(self):
        params = {"admin_c": [self.contacts[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_tech_c(self):
        params = {"tech_c": [self.contacts[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tech_c": [self.contacts[0], self.contacts[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_billing_c(self):
        params = {"billing_c": [self.contacts[0]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"billing_c": [self.contacts[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"billing_c": [self.contacts[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"billing_c": [self.contacts[1], self.contacts[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
