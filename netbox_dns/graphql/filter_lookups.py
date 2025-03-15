import strawberry

from netbox.graphql.filter_lookups import ArrayLookup

from netbox_dns.graphql.enums import NetBoxDNSDNSSECPolicyDigestEnum


@strawberry.input(
    one_of=True,
    description="Lookup for Array fields. Only one of the lookup fields can be set.",
)
class PolicyDigestArrayLookup(ArrayLookup[NetBoxDNSDNSSECPolicyDigestEnum]):
    pass
