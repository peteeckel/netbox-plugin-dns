from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer

from netbox_dns.api.nested_serializers import (
    NestedViewSerializer,
    NestedZoneSerializer,
    NestedNameServerSerializer,
    NestedRecordSerializer,
)
from netbox_dns.models import View, Zone, NameServer, Record


class ViewSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:view-detail"
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = View
        fields = (
            "id",
            "url",
            "display",
            "name",
            "tags",
            "description",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
        )


class ZoneSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    view = NestedViewSerializer(
        many=False,
        read_only=False,
        required=False,
        default=None,
        help_text="View the zone belongs to",
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
    active = serializers.BooleanField(
        required=False,
        read_only=True,
        allow_null=True,
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    def create(self, validated_data):
        nameservers = validated_data.pop("nameservers", None)

        zone = super().create(validated_data)

        if nameservers is not None:
            zone.nameservers.set(nameservers)

        return zone

    def update(self, instance, validated_data):
        nameservers = validated_data.pop("nameservers", None)

        zone = super().update(instance, validated_data)

        if nameservers is not None:
            zone.nameservers.set(nameservers)

        return zone

    class Meta:
        model = Zone
        fields = (
            "id",
            "url",
            "name",
            "view",
            "display",
            "nameservers",
            "status",
            "description",
            "tags",
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
            "active",
            "custom_fields",
            "tenant",
        )


class NameServerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:nameserver-detail"
    )
    zones = NestedZoneSerializer(
        many=True,
        read_only=True,
        required=False,
        default=None,
        help_text="Zones served by the authoritative nameserver",
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = NameServer
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "tags",
            "zones",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
        )


class RecordSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:record-detail"
    )
    ptr_record = NestedRecordSerializer(
        many=False,
        read_only=True,
        required=False,
        allow_null=True,
        help_text="PTR record generated from an address",
    )
    address_record = NestedRecordSerializer(
        many=False,
        read_only=True,
        required=False,
        allow_null=True,
        help_text="Address record defining the PTR",
    )
    zone = NestedZoneSerializer(
        many=False,
        required=False,
        help_text="Zone the record belongs to",
    )
    active = serializers.BooleanField(
        required=False,
        read_only=True,
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)

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
            "status",
            "ttl",
            "description",
            "tags",
            "created",
            "last_updated",
            "managed",
            "disable_ptr",
            "ptr_record",
            "address_record",
            "active",
            "custom_fields",
            "tenant",
        )
