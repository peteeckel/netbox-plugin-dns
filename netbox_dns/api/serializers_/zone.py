from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.api.serializers_.view import ViewSerializer
from netbox_dns.api.serializers_.nameserver import NameServerSerializer
from netbox_dns.api.serializers_.registrar import RegistrarSerializer
from netbox_dns.api.serializers_.contact import ContactSerializer
from netbox_dns.api.nested_serializers import NestedZoneSerializer

from netbox_dns.models import Zone


class ZoneSerializer(NetBoxModelSerializer):
    # +
    # This is a hack to avoid the exception raised by the UniqueTogetherValidator
    # after NetBox commit https://github.com/netbox-community/netbox/commit/78e284c
    #
    # See https://github.com/netbox-community/netbox/issues/15351 for details.
    # -
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.nested:
            self.validators = []

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    view = ViewSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        default=None,
        help_text="View the zone belongs to",
    )
    nameservers = NameServerSerializer(
        nested=True,
        many=True,
        read_only=False,
        required=False,
        help_text="Nameservers for the zone",
    )
    soa_mname = NameServerSerializer(
        nested=True,
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
    registrar = RegistrarSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text="The registrar the domain is registered with",
    )
    registrant = ContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The owner of the domain",
    )
    admin_c = ContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The administrative contact for the domain",
    )
    tech_c = ContactSerializer(
        many=False,
        read_only=False,
        required=False,
        help_text="The technical contact for the domain",
    )
    billing_c = ContactSerializer(
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
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

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
        brief_fields = (
            "id",
            "url",
            "name",
            "view",
            "display",
            "status",
            "description",
            "rfc2317_prefix",
            "active",
        )
