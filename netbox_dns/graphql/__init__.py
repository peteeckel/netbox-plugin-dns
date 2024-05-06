from .schema import (
    NetBoxDNSViewQuery,
    NetBoxDNSNameServerQuery,
    NetBoxDNSContactQuery,
    NetBoxDNSRegistrarQuery,
    NetBoxDNSZoneQuery,
    NetBoxDNSRecordQuery,
)

schema = [
    NetBoxDNSNameServerQuery,
    NetBoxDNSViewQuery,
    NetBoxDNSZoneQuery,
    NetBoxDNSRecordQuery,
    NetBoxDNSContactQuery,
    NetBoxDNSRegistrarQuery,
]
