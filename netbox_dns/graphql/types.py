from typing import Annotated, List

import strawberry
import strawberry_django

from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType
from ipam.graphql.types import IPAddressType, PrefixType
from netbox.graphql.scalars import BigInt

from netbox_dns.models import (
    NameServer,
    View,
    Zone,
    Record,
    DNSSECKeyTemplate,
    DNSSECPolicy,
    RegistrationContact,
    Registrar,
    ZoneTemplate,
    RecordTemplate,
)
from .filters import (
    NetBoxDNSNameServerFilter,
    NetBoxDNSViewFilter,
    NetBoxDNSZoneFilter,
    NetBoxDNSRecordFilter,
    NetBoxDNSDNSSECKeyTemplateFilter,
    NetBoxDNSDNSSECPolicyFilter,
    NetBoxDNSRegistrationContactFilter,
    NetBoxDNSRegistrarFilter,
    NetBoxDNSZoneTemplateFilter,
    NetBoxDNSRecordTemplateFilter,
)


@strawberry_django.type(NameServer, fields="__all__", filters=NetBoxDNSNameServerFilter)
class NetBoxDNSNameServerType(NetBoxObjectType):
    name: str
    description: str
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    soa_zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]


@strawberry_django.type(View, fields="__all__", filters=NetBoxDNSViewFilter)
class NetBoxDNSViewType(NetBoxObjectType):
    name: str
    description: str
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    prefixes: List[Annotated["PrefixType", strawberry.lazy("ipam.graphql.types")]]
    ip_address_filter: str | None
    zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]


@strawberry_django.type(Zone, fields="__all__", filters=NetBoxDNSZoneFilter)
class NetBoxDNSZoneType(NetBoxObjectType):
    name: str
    description: str | None
    status: str
    active: bool
    view: Annotated["NetBoxDNSViewType", strawberry.lazy("netbox_dns.graphql.types")]
    nameservers: List[
        Annotated[
            "NetBoxDNSNameServerType", strawberry.lazy("netbox_dns.graphql.types")
        ]
    ]
    default_ttl: BigInt
    soa_ttl: BigInt
    soa_mname: Annotated[
        "NetBoxDNSNameServerType", strawberry.lazy("netbox_dns.graphql.types")
    ]
    soa_rname: str
    soa_serial: BigInt
    soa_refresh: BigInt
    soa_retry: BigInt
    soa_expire: BigInt
    soa_minimum: BigInt
    soa_serial_auto: bool
    dnssec_policy: (
        Annotated[
            "NetBoxDNSDNSSECPolicyType", strawberry.lazy("netbox_dns.graphql.types")
        ]
        | None
    )
    inline_signing: bool
    parental_agents: List[str]
    registrar: (
        Annotated["NetBoxDNSRegistrarType", strawberry.lazy("netbox_dns.graphql.types")]
        | None
    )
    registry_domain_id: str | None
    registrant: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    admin_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    tech_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    billing_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    rfc2317_prefix: str | None
    rfc2317_parent_managed: str
    rfc2317_parent_zone: (
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
        | None
    )
    records: List[
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    rfc2317_child_zones: List[
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    arpa_network: str | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None


@strawberry_django.type(Record, fields="__all__", filters=NetBoxDNSRecordFilter)
class NetBoxDNSRecordType(NetBoxObjectType):
    name: str
    zone: Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    type: str
    value: str
    absolute_value: str
    status: str
    ttl: BigInt | None
    managed: bool
    ptr_record: (
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
        | None
    )
    disable_ptr: bool
    description: str | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    ip_address: str | None
    ipam_ip_address: (
        Annotated["IPAddressType", strawberry.lazy("ipam.graphql.types")] | None
    )
    rfc2317_cname_record: (
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
        | None
    )
    address_records: List[
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    rfc2317_ptr_records: List[
        Annotated["NetBoxDNSRecordType", strawberry.lazy("netbox_dns.graphql.types")]
    ]


@strawberry_django.type(
    DNSSECKeyTemplate, fields="__all__", filters=NetBoxDNSDNSSECKeyTemplateFilter
)
class NetBoxDNSDNSSECKeyTemplateType(NetBoxObjectType):
    name: str
    description: str
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    type: str
    lifetime: BigInt | None
    algorithm: str
    key_size: BigInt | None


@strawberry_django.type(
    DNSSECPolicy, fields="__all__", filters=NetBoxDNSDNSSECPolicyFilter
)
class NetBoxDNSDNSSECPolicyType(NetBoxObjectType):
    name: str
    description: str | None
    status: str
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    key_templates: List[
        Annotated[
            "NetBoxDNSDNSSECKeyTemplateType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
    ]
    dnskey_ttl: BigInt | None
    purge_keys: BigInt | None
    publish_safety: BigInt | None
    retire_safety: BigInt | None
    signatures_jitter: BigInt | None
    signatures_refresh: BigInt | None
    signatures_validity: BigInt | None
    signatures_validity_dnskey: BigInt | None
    max_zone_ttl: BigInt | None
    zone_propagation_delay: BigInt | None
    create_cdnskey: bool
    cds_digest_types: List[str]
    parent_ds_ttl: BigInt | None
    parent_propagation_delay: BigInt | None
    use_nsec3: bool
    nsec3_iterations: BigInt | None
    nsec3_opt_out: bool
    nsec3_salt_size: BigInt | None


@strawberry_django.type(
    RegistrationContact, fields="__all__", filters=NetBoxDNSRegistrationContactFilter
)
class NetBoxDNSRegistrationContactType(NetBoxObjectType):
    name: str
    contact_id: str
    description: str
    organization: str
    street: str
    city: str
    state_province: str
    postal_code: str
    country: str
    phone: str
    phone_ext: str
    fax: str
    fax_ext: str
    email: str
    registrant_zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    admin_c_zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    tech_c_zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]
    billing_c_zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]


@strawberry_django.type(Registrar, fields="__all__", filters=NetBoxDNSRegistrarFilter)
class NetBoxDNSRegistrarType(NetBoxObjectType):
    name: str
    description: str
    iana_id: int
    referral_url: str
    whois_server: str
    address: str
    abuse_email: str
    abuse_phone: str
    zones: List[
        Annotated["NetBoxDNSZoneType", strawberry.lazy("netbox_dns.graphql.types")]
    ]


@strawberry_django.type(
    ZoneTemplate, fields="__all__", filters=NetBoxDNSZoneTemplateFilter
)
class NetBoxDNSZoneTemplateType(NetBoxObjectType):
    name: str
    nameservers: List[
        Annotated[
            "NetBoxDNSNameServerType", strawberry.lazy("netbox_dns.graphql.types")
        ]
    ]
    soa_mname: (
        Annotated[
            "NetBoxDNSNameServerType", strawberry.lazy("netbox_dns.graphql.types")
        ]
        | None
    )
    soa_rname: str | None
    dnssec_policy: (
        Annotated[
            "NetBoxDNSDNSSECPolicyType", strawberry.lazy("netbox_dns.graphql.types")
        ]
        | None
    )
    record_templates: List[
        Annotated[
            "NetBoxDNSRecordTemplateType", strawberry.lazy("netbox_dns.graphql.types")
        ]
    ]
    description: str | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    registrar: (
        Annotated["NetBoxDNSRegistrarType", strawberry.lazy("netbox_dns.graphql.types")]
        | None
    )
    registrant: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    admin_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    tech_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )
    billing_c: (
        Annotated[
            "NetBoxDNSRegistrationContactType",
            strawberry.lazy("netbox_dns.graphql.types"),
        ]
        | None
    )


@strawberry_django.type(
    RecordTemplate, fields="__all__", filters=NetBoxDNSRecordTemplateFilter
)
class NetBoxDNSRecordTemplateType(NetBoxObjectType):
    name: str
    record_name: str
    type: str
    value: str
    ttl: BigInt | None
    disable_ptr: bool
    description: str | None
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    zone_templates: List[
        Annotated[
            "NetBoxDNSZoneTemplateType", strawberry.lazy("netbox_dns.graphql.types")
        ]
    ]
