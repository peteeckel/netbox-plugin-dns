import strawberry

from netbox_dns.choices import (
    RecordTypeChoices,
    RecordClassChoices,
    RecordStatusChoices,
    ZoneStatusChoices,
)

__all__ = (
    "NetBoxDNSRecordTypeEnum",
    "NetBoxDNSRecordClassEnum",
    "NetBoxDNSRecordStatusEnum",
    "NetBoxDNSZoneStatusEnum",
)

NetBoxDNSRecordTypeEnum = strawberry.enum(RecordTypeChoices.as_enum())
NetBoxDNSRecordClassEnum = strawberry.enum(RecordClassChoices.as_enum())
NetBoxDNSRecordStatusEnum = strawberry.enum(RecordStatusChoices.as_enum())
NetBoxDNSZoneStatusEnum = strawberry.enum(ZoneStatusChoices.as_enum())
