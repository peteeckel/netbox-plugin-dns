from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup

from netbox_dns.models import Registrar


__all__ = ("NetBoxDNSRegistrarFilter",)


@strawberry_django.filter_type(Registrar, lookups=True)
class NetBoxDNSRegistrarFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    iana_id: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    address: FilterLookup[str] | None = strawberry_django.filter_field()
    referral_url: FilterLookup[str] | None = strawberry_django.filter_field()
    whois_server: FilterLookup[str] | None = strawberry_django.filter_field()
    abuse_email: FilterLookup[str] | None = strawberry_django.filter_field()
    abuse_phone: FilterLookup[str] | None = strawberry_django.filter_field()
