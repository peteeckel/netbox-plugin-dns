from typing import List

import strawberry
import strawberry_django

from netbox_dns.models import NameServer, View, Zone, Record, Contact, Registrar
from .types import (
    NetBoxDNSNameServerType,
    NetBoxDNSViewType,
    NetBoxDNSZoneType,
    NetBoxDNSRecordType,
    NetBoxDNSContactType,
    NetBoxDNSRegistrarType,
)


@strawberry.type
class NetBoxDNSNameServerQuery:
    @strawberry.field
    def netbox_dns_nameserver(self, id: int) -> NetBoxDNSNameServerType:
        return NameServer.objects.get(pk=id)

    netbox_dns_nameserver_list: List[NetBoxDNSNameServerType] = (
        strawberry_django.field()
    )


@strawberry.type
class NetBoxDNSViewQuery:
    @strawberry.field
    def netbox_dns_view(self, id: int) -> NetBoxDNSViewType:
        return View.objects.get(pk=id)

    netbox_dns_view_list: List[NetBoxDNSViewType] = strawberry_django.field()


@strawberry.type
class NetBoxDNSZoneQuery:
    @strawberry.field
    def netbox_dns_zone(self, id: int) -> NetBoxDNSZoneType:
        return Zone.objects.get(pk=id)

    netbox_dns_zone_list: List[NetBoxDNSZoneType] = strawberry_django.field()


@strawberry.type
class NetBoxDNSRecordQuery:
    @strawberry.field
    def netbox_dns_record(self, id: int) -> NetBoxDNSRecordType:
        return Record.objects.get(pk=id)

    netbox_dns_record_list: List[NetBoxDNSRecordType] = strawberry_django.field()


@strawberry.type
class NetBoxDNSContactQuery:
    @strawberry.field
    def netbox_dns_contact(self, id: int) -> NetBoxDNSContactType:
        return Contact.objects.get(pk=id)

    netbox_dns_contact_list: List[NetBoxDNSContactType] = strawberry_django.field()


@strawberry.type
class NetBoxDNSRegistrarQuery:
    @strawberry.field
    def netbox_dns_registrar(self, id: int) -> NetBoxDNSRegistrarType:
        return Registrar.objects.get(pk=id)

    netbox_dns_registrar_list: List[NetBoxDNSRegistrarType] = strawberry_django.field()
