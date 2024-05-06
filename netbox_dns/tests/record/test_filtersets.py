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


class RecordFilterSetTestCase(TestCase, ChangeLoggedFilterSetTests):
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
        for zone in cls.zones:
            zone.save()

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
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

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
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

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

    def test_ip_address(self):
        params = {"ip_address": ["fe80::dead:beef", "10.0.0.42", "1.2.3.4"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"ip_address": ["10.0.0.42"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"ip_address": ["fe80::dead:beef"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_ptr_record(self):
        Zone(
            name="1.0.10.in-addr.arpa", soa_mname=self.nameservers[0], **self.zone_data
        ).save()
        address_record = Record(
            name="name4",
            zone=self.zones[0],
            type=RecordTypeChoices.A,
            disable_ptr=False,
            value="10.0.1.42",
        )
        address_record.save()

        ptr_record = Record.objects.get(address_record=address_record)
        params = {"ptr_record_id": [ptr_record.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        self.assertEqual(
            self.filterset(params, self.queryset).qs.first().pk, address_record.pk
        )

    def test_rfc2317_cname_record(self):
        ptr_zone = Zone(
            name="1.0.10.in-addr.arpa", soa_mname=self.nameservers[0], **self.zone_data
        )
        ptr_zone.save()
        rfc2317_zone = Zone(
            name="0-31.1.0.10.in-addr.arpa",
            soa_mname=self.nameservers[0],
            rfc2317_prefix="10.0.1.0/27",
            rfc2317_parent_managed=True,
            **self.zone_data
        )
        rfc2317_zone.save()
        address_record = Record(
            name="name4",
            zone=self.zones[0],
            type=RecordTypeChoices.A,
            disable_ptr=False,
            value="10.0.1.23",
        )
        address_record.save()

        ptr_record = Record.objects.get(address_record=address_record)
        cname_record = ptr_record.rfc2317_cname_record
        params = {"rfc2317_cname_record_id": [cname_record.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        self.assertEqual(
            self.filterset(params, self.queryset).qs.first().pk, ptr_record.pk
        )
