from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from ipam.api.serializers import IPAddressSerializer
from tenancy.api.serializers import TenantSerializer

from netbox_dns.models import Record

from ..nested_serializers import NestedZoneSerializer, NestedRecordSerializer
from ..field_serializers import TimePeriodField


__all__ = ("RecordSerializer",)


class RecordSerializer(NetBoxModelSerializer):
    class Meta:
        model = Record
        fields = (
            "id",
            "url",
            "zone",
            "display",
            "type",
            "name",
            "fqdn",
            "value",
            "status",
            "ttl",
            "description",
            "tags",
            "created",
            "last_updated",
            "managed",
            "disable_ptr",
            "ptr_record",
            "address_records",
            "active",
            "custom_fields",
            "tenant",
            "ipam_ip_address",
            "absolute_value",
        )

        brief_fields = (
            "id",
            "url",
            "zone",
            "display",
            "type",
            "name",
            "fqdn",
            "value",
            "status",
            "ttl",
            "description",
            "managed",
            "active",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:record-detail"
    )
    ttl = TimePeriodField(
        required=False,
        allow_null=True,
    )
    ptr_record = NestedRecordSerializer(
        many=False,
        read_only=True,
        required=False,
        allow_null=True,
        help_text=_("PTR record related to an address"),
    )
    address_records = NestedRecordSerializer(
        many=True,
        read_only=True,
        required=False,
        allow_null=True,
        help_text=_("Address records related to the PTR"),
    )
    zone = NestedZoneSerializer(
        many=False,
        required=False,
        help_text=_("Zone the record belongs to"),
    )
    active = serializers.BooleanField(
        required=False,
        read_only=True,
    )
    ipam_ip_address = IPAddressSerializer(
        nested=True,
        many=False,
        read_only=True,
        required=False,
        allow_null=True,
        help_text=_("IPAddress linked to the record"),
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )
