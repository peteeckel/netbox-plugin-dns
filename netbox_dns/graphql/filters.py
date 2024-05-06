import strawberry_django

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

from netbox_dns.models import NameServer, View, Zone, Record, Contact, Registrar
from netbox_dns.filtersets import (
    NameServerFilterSet,
    ViewFilterSet,
    ZoneFilterSet,
    RecordFilterSet,
    ContactFilterSet,
    RegistrarFilterSet,
)


@strawberry_django.filter(NameServer, lookups=True)
@autotype_decorator(NameServerFilterSet)
class NetBoxDNSNameServerFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(View, lookups=True)
@autotype_decorator(ViewFilterSet)
class NetBoxDNSViewFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(Zone, lookups=True)
@autotype_decorator(ZoneFilterSet)
class NetBoxDNSZoneFilter(BaseFilterMixin):
    rfc2317_prefix: str | None


@strawberry_django.filter(Record, lookups=True)
@autotype_decorator(RecordFilterSet)
class NetBoxDNSRecordFilter(BaseFilterMixin):
    ip_address: str | None


@strawberry_django.filter(Contact, lookups=True)
@autotype_decorator(ContactFilterSet)
class NetBoxDNSContactFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(Registrar, lookups=True)
@autotype_decorator(RegistrarFilterSet)
class NetBoxDNSRegistrarFilter(BaseFilterMixin):
    pass
