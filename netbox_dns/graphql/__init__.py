from .schema import (
    NetBoxDNSViewQuery,
    NetBoxDNSNameServerQuery,
    NetBoxDNSContactQuery,
    NetBoxDNSRegistrarQuery,
    NetBoxDNSZoneQuery,
    NetBoxDNSRecordQuery,
    NetBoxDNSZoneTemplateQuery,
    NetBoxDNSRecordTemplateQuery,
)

schema = [
    NetBoxDNSNameServerQuery,
    NetBoxDNSViewQuery,
    NetBoxDNSZoneQuery,
    NetBoxDNSRecordQuery,
    NetBoxDNSContactQuery,
    NetBoxDNSRegistrarQuery,
    NetBoxDNSZoneTemplateQuery,
    NetBoxDNSRecordTemplateQuery,
]
