from .schema import (
    NetBoxDNSViewQuery,
    NetBoxDNSNameServerQuery,
    NetBoxDNSRegistrationContactQuery,
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
    NetBoxDNSRegistrationContactQuery,
    NetBoxDNSRegistrarQuery,
    NetBoxDNSZoneTemplateQuery,
    NetBoxDNSRecordTemplateQuery,
]
