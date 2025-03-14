import strawberry

from netbox_dns.choices import (
    RecordTypeChoices,
    RecordClassChoices,
    RecordStatusChoices,
    ZoneStatusChoices,
    DNSSECPolicyDigestChoices,
    DNSSECPolicyStatusChoices,
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)

__all__ = (
    "NetBoxDNSRecordTypeEnum",
    "NetBoxDNSRecordClassEnum",
    "NetBoxDNSRecordStatusEnum",
    "NetBoxDNSZoneStatusEnum",
    "NetBoxDNSDNSSECPolicyDigestEnum",
    "NetBoxDNSDNSSECPolicyStatusEnum",
    "NetBoxDNSDNSSECKeyTemplateTypeEnum",
    "NetBoxDNSDNSSECKeyTemplateAlgorithmEnum",
    "NetBoxDNSDNSSECKeyTemplateKeySizeEnum",
)

NetBoxDNSRecordTypeEnum = strawberry.enum(RecordTypeChoices.as_enum())
NetBoxDNSRecordClassEnum = strawberry.enum(RecordClassChoices.as_enum())
NetBoxDNSRecordStatusEnum = strawberry.enum(RecordStatusChoices.as_enum())
NetBoxDNSZoneStatusEnum = strawberry.enum(ZoneStatusChoices.as_enum())
NetBoxDNSDNSSECPolicyDigestEnum = strawberry.enum(DNSSECPolicyDigestChoices.as_enum())
NetBoxDNSDNSSECPolicyStatusEnum = strawberry.enum(DNSSECPolicyStatusChoices.as_enum())
NetBoxDNSDNSSECKeyTemplateTypeEnum = strawberry.enum(
    DNSSECKeyTemplateTypeChoices.as_enum()
)
NetBoxDNSDNSSECKeyTemplateAlgorithmEnum = strawberry.enum(
    DNSSECKeyTemplateAlgorithmChoices.as_enum()
)
NetBoxDNSDNSSECKeyTemplateKeySizeEnum = strawberry.enum(
    DNSSECKeyTemplateKeySizeChoices.as_enum()
)
