from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin

if TYPE_CHECKING:
    from ipam.graphql.filters import PrefixFilter, IPAddressFilter
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import (
        NetBoxDNSZoneStatusEnum,
        NetBoxDNSRecordStatusEnum,
        NetBoxDNSRecordTypeEnum,
        NetBoxDNSDNSSECPolicyDigestEnum,
        NetBoxDNSDNSSECPolicyStatusEnum,
        NetBoxDNSDNSSECKeyTemplateTypeEnum,
        NetBoxDNSDNSSECKeyTemplateAlgorithmEnum,
        NetBoxDNSDNSSECKeyTemplateKeySizeEnum,
    )

from netbox_dns.models import (
    NameServer,
    View,
    Zone,
    Record,
    RegistrationContact,
    Registrar,
    ZoneTemplate,
    RecordTemplate,
    DNSSECKeyTemplate,
    DNSSECPolicy,
)


@strawberry_django.filter(NameServer, lookups=True)
class NetBoxDNSNameServerFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    zones: (
        Annotated["NetBoxDNSZoneFilter", strawberry.lazy("netbox_dns.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(View, lookups=True)
class NetBoxDNSViewFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    default_view: FilterLookup[bool] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    prefixes: (
        Annotated["PrefixFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(Zone, lookups=True)
class NetBoxDNSZoneFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    view: (
        Annotated["NetBoxDNSViewFilter", strawberry.lazy("netbox_dns.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    view_id: ID | None = strawberry_django.filter_field()
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
    default_ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()

    soa_ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
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
    soa_serial: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    soa_refresh: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    soa_retry: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    soa_expire: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    soa_minimum: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    soa_serial_auto: FilterLookup[bool] | None = strawberry_django.filter_field()

    registrar: (
        Annotated[
            "NetBoxDNSRegistrarFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    )
    registrar_id: ID | None = strawberry_django.filter_field()
    registry_domain_id: FilterLookup[str] | None = strawberry_django.filter_field()
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

    rfc2317_prefix: FilterLookup[str] | None = strawberry_django.filter_field()
    rfc2317_parent_zone: (
        Annotated["NetBoxDNSZoneFilter", strawberry.lazy("netbox_dns.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    rfc2317_parent_zone_id: ID | None = strawberry_django.filter_field()
    rfc2317_parent_managed: FilterLookup[bool] | None = strawberry_django.filter_field()

    arpa_network: FilterLookup[str] | None = strawberry_django.filter_field()
    active: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter(Record, lookups=True)
class NetBoxDNSRecordFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    fqdn: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    view: (
        Annotated["NetBoxDNSViewFilter", strawberry.lazy("netbox_dns.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    view_id: ID | None = strawberry_django.filter_field()
    zone: (
        Annotated["NetBoxDNSZoneFilter", strawberry.lazy("netbox_dns.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    zone_id: ID | None = strawberry_django.filter_field()
    type: (
        Annotated[
            "NetBoxDNSRecordTypeEnum", strawberry.lazy("netbox_dns.graphql.enums")
        ]
        | None
    ) = strawberry_django.filter_field()
    ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    value: FilterLookup[str] | None = strawberry_django.filter_field()
    disable_ptr: FilterLookup[bool] | None = strawberry_django.filter_field()
    status: (
        Annotated[
            "NetBoxDNSRecordStatusEnum", strawberry.lazy("netbox_dns.graphql.enums")
        ]
        | None
    ) = strawberry_django.filter_field()
    managed: FilterLookup[bool] | None = strawberry_django.filter_field()
    address_record: (
        Annotated[
            "NetBoxDNSRecordFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    address_record_id: ID | None = strawberry_django.filter_field()
    ptr_record: (
        Annotated[
            "NetBoxDNSRecordFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    ptr_record_id: ID | None = strawberry_django.filter_field()
    rfc2317_cname_record: (
        Annotated[
            "NetBoxDNSRecordFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    ipam_ip_address: (
        Annotated["IPAddressFilter", strawberry.lazy("ipam.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    ipam_ip_address_id: ID | None = strawberry_django.filter_field()

    ip_address: FilterLookup[str] | None = strawberry_django.filter_field()
    active: FilterLookup[bool] | None = strawberry_django.filter_field()


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


@strawberry_django.filter(RecordTemplate, lookups=True)
class NetBoxDNSRecordTemplateFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    record_name: FilterLookup[str] | None = strawberry_django.filter_field()
    type: (
        Annotated[
            "NetBoxDNSRecordTypeEnum", strawberry.lazy("netbox_dns.graphql.enums")
        ]
        | None
    ) = strawberry_django.filter_field()
    status: (
        Annotated[
            "NetBoxDNSRecordStatusEnum", strawberry.lazy("netbox_dns.graphql.enums")
        ]
        | None
    ) = strawberry_django.filter_field()
    ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    value: FilterLookup[str] | None = strawberry_django.filter_field()
    disable_ptr: FilterLookup[bool] | None = strawberry_django.filter_field()

    zone_templates: (
        Annotated[
            "NetBoxDNSRecordTemplateFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(DNSSECKeyTemplate, lookups=True)
class NetBoxDNSDNSSECKeyTemplateFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    type: (
        Annotated[
            "NetBoxDNSDNSSECKeyTemplateTypeEnum",
            strawberry.lazy("netbox_dns.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    algorithm: (
        Annotated[
            "NetBoxDNSDNSSECKeyTemplateAlgorithmEnum",
            strawberry.lazy("netbox_dns.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    lifetime: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    key_size: (
        Annotated[
            "NetBoxDNSDNSSECKeyTemplateKeySizeEnum",
            strawberry.lazy("netbox_dns.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    policy: (
        Annotated[
            "NetBoxDNSDNSSECPolicyFilter", strawberry.lazy("netbox_dns.graphql.filters")
        ]
        | None
    ) = strawberry_django.filter_field()
    policy_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(DNSSECPolicy, lookups=True)
class NetBoxDNSDNSSECPolicyFilter(
    ContactFilterMixin, TenancyFilterMixin, NetBoxModelFilterMixin
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    status: (
        Annotated[
            "NetBoxDNSDNSSECPolicyStatusEnum",
            strawberry.lazy("netbox_dns.graphql.enums"),
        ]
        | None
    ) = strawberry_django.filter_field()
    key_template: (
        Annotated[
            "NetBoxDNSDNSSECKeyTemplateFilter",
            strawberry.lazy("netbox_dns.graphql.filters"),
        ]
        | None
    ) = strawberry_django.filter_field()
    dnskey_ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    purge_keys: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    publish_safety: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    retire_safety: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    signatures_jitter: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    signatures_refresh: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    signatures_validity: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    signatures_validity_dnskey: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    max_zone_ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    zone_propagation_delay: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
#
# TODO: FIx this (GraphQL filtzer for ArrayField)
#
#    cds_digest_types: (
#        Annotated[
#            "NetBoxDNSDNSSECPolicyDigestEnum",
#            strawberry.lazy("netbox_dns.graphql.enums"),
#        ]
#        | None
#    ) = strawberry_django.filter_field()
    create_cdnskey: FilterLookup[bool] | None = strawberry_django.filter_field()
    parent_ds_ttl: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    parent_propagation_delay: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    use_nsec3: FilterLookup[bool] | None = strawberry_django.filter_field()
    nsec3_iterations: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()
    nsec3_opt_out: FilterLookup[bool] | None = strawberry_django.filter_field()
    nsec3_salt_size: (
        Annotated["IntegerLookup", strawberry.lazy("netbox.graphql.filter_lookups")]
        | None
    ) = strawberry_django.filter_field()


@strawberry_django.filter(Registrar, lookups=True)
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


@strawberry_django.filter(RegistrationContact, lookups=True)
class NetBoxDNSRegistrationContactFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    contact_id: FilterLookup[str] | None = strawberry_django.filter_field()
    organization: FilterLookup[str] | None = strawberry_django.filter_field()
    street: FilterLookup[str] | None = strawberry_django.filter_field()
    city: FilterLookup[str] | None = strawberry_django.filter_field()
    state_province: FilterLookup[str] | None = strawberry_django.filter_field()
    postal_code: FilterLookup[str] | None = strawberry_django.filter_field()
    country: FilterLookup[str] | None = strawberry_django.filter_field()
    phone: FilterLookup[str] | None = strawberry_django.filter_field()
    phone_ext: FilterLookup[str] | None = strawberry_django.filter_field()
    fax: FilterLookup[str] | None = strawberry_django.filter_field()
    fax_ext: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
