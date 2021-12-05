from rest_framework import serializers

from netbox.api.serializers import PrimaryModelSerializer
from netbox_dns.api.nested_serializers import (
    NestedRecordSerializer,
    NestedNameServerSerializer,
)
from netbox_dns.models import Record, Zone, NameServer


class NameServerSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:nameserver-detail"
    )

    class Meta:
        model = NameServer
        fields = (
            "id",
            "url",
            "display",
            "name",
            "tags",
            "custom_field_data",
            "created",
            "last_updated",
        )


class RecordSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:record-detail"
    )
    ptr_record = NestedRecordSerializer(
        many=False,
        read_only=True,
        required=False,
        help_text="PTR record generated from an address",
    )
    address_record = NestedRecordSerializer(
        many=False,
        read_only=True,
        required=False,
        help_text="Address record defining the PTR",
    )

    class Meta:
        model = Record
        fields = (
            "id",
            "url",
            "zone",
            "display",
            "type",
            "name",
            "value",
            "ttl",
            "tags",
            "custom_field_data",
            "created",
            "last_updated",
            "managed",
            "disable_ptr",
            "ptr_record",
            "address_record",
        )


class ZoneSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    nameservers = NestedNameServerSerializer(
        many=True, read_only=False, required=False, help_text="Nameservers for the zone"
    )
    soa_mname = NestedNameServerSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="Primary nameserver for the zone",
    )

    class Meta:
        model = Zone
        fields = (
            "id",
            "url",
            "name",
            "display",
            "nameservers",
            "status",
            "nameservers",
            "tags",
            "custom_field_data",
            "created",
            "last_updated",
            "default_ttl",
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial",
            "soa_serial_auto",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
        )
