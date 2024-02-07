from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer

from netbox_dns.api.nested_serializers import (
    NestedViewSerializer,
    NestedZoneSerializer,
    NestedNameServerSerializer,
    NestedRecordSerializer,
    NestedRegistrarSerializer,
    NestedContactSerializer,
)
from netbox_dns.models import View, Zone, NameServer, Record, Registrar, Contact


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
    rfc2317_parent_zone = NestedZoneSerializer(
        many=False,
        read_only=True,
        required=False,
        help_text="RFC2317 arent zone for the zone",
    )
    rfc2317_child_zones = NestedZoneSerializer(
        many=True,
        read_only=True,
        required=False,
        help_text="RFC2317 child zones of the zone",
    )
    registrar = NestedRegistrarSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The registrar the domain is registered with",
    )
    registrant = NestedContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The owner of the domain",
    )
    admin_c = NestedContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The administrative contact for the domain",
    )
    tech_c = NestedContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The technical contact for the domain",
    )
    billing_c = NestedContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The billing contact for the domain",
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
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            "rfc2317_parent_zone",
            "rfc2317_child_zones",
            "registrar",
            "registry_domain_id",
            "registrant",
            "tech_c",
            "admin_c",
            "billing_c",
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
    ipam_ip_address = NestedIPAddressSerializer(
        many=False,
        read_only=True,
        required=False,
        allow_null=True,
        help_text="IPAddress linked to the record",
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
            "ipam_ip_address",
        )


class RegistrarSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:registrar-detail"
    )

    class Meta:
        model = Registrar
        fields = (
            "id",
            "url",
            "display",
            "name",
            "iana_id",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "created",
            "last_updated",
            "custom_fields",
        )


class ContactSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:contact-detail"
    )

    class Meta:
        model = Contact
        fields = (
            "id",
            "url",
            "display",
            "name",
            "contact_id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
            "created",
            "last_updated",
            "custom_fields",
        )
