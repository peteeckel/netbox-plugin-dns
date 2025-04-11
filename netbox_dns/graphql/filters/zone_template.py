from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin

if TYPE_CHECKING:
    from .enums import NetBoxDNSZoneStatusEnum
    from .nameserver import NetBoxDNSNameServerFilter
    from .record_template import NetBoxDNSRecordTemplateFilter
    from .registrar import NetBoxDNSRegistrarFilter
    from .registration_contact import NetBoxDNSRegistrationContactFilter

from netbox_dns.models import ZoneTemplate


__all__ = ("NetBoxDNSZoneTemplateFilter",)


@strawberry_django.filter(ZoneTemplate, lookups=True)
class NetBoxDNSZoneTemplateFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    nameservers: (
        Annotated[
            "NetBoxDNSNameServerFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    status: (
        Annotated[
            "NetBoxDNSZoneStatusEnum", strawberry.lazy("netbox_dns.graphql.enums")
        ]
        | None
    ) = strawberry_django.filter_field()

    soa_mname: (
        Annotated[
            "NetBoxDNSNameServerFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    soa_mname_id: ID | None = strawberry_django.filter_field()
    soa_rname: FilterLookup[str] | None = strawberry_django.filter_field()

    registrar: (
        Annotated[
            "NetBoxDNSRegistrarFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    )
    registrar_id: ID | None = strawberry_django.filter_field()
    registrant: (
        Annotated[
            "NetBoxDNSRegistrationContactFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    )
    registrant_id: ID | None = strawberry_django.filter_field()
    admin_c: (
        Annotated[
            "NetBoxDNSRegistrationContactFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    )
    admin_c_id: ID | None = strawberry_django.filter_field()
    tech_c: (
        Annotated[
            "NetBoxDNSRegistrationContactFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    )
    tech_c_id: ID | None = strawberry_django.filter_field()
    billing_c: (
        Annotated[
            "NetBoxDNSRegistrationContactFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    )
    billing_c_id: ID | None = strawberry_django.filter_field()
    record_templates: (
        Annotated[
            "NetBoxDNSRecordTemplateFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
