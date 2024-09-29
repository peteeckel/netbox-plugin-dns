from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer

from .view import ViewSerializer
from .nameserver import NameServerSerializer
from .registrar import RegistrarSerializer
from .registration_contact import RegistrationContactSerializer
from .zone_template import ZoneTemplateSerializer

from ..nested_serializers import NestedZoneSerializer

from netbox_dns.models import Zone


__all__ = ("ZoneSerializer",)


class ZoneSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    view = ViewSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        default=None,
        help_text=_("View the zone belongs to"),
    )
    nameservers = NameServerSerializer(
        nested=True,
        many=True,
        read_only=False,
        required=False,
        help_text=_("Nameservers for the zone"),
    )
    soa_mname = NameServerSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Primary nameserver for the zone"),
    )
    rfc2317_parent_zone = NestedZoneSerializer(
        many=False,
        read_only=True,
        required=False,
        help_text=_("RFC2317 parent zone of the zone"),
    )
    rfc2317_child_zones = NestedZoneSerializer(
        many=True,
        read_only=True,
        required=False,
        help_text=_("RFC2317 child zones of the zone"),
    )
    registrar = RegistrarSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Registrar the domain is registered with"),
    )
    registrant = RegistrationContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Registrant of the domain"),
    )
    admin_c = RegistrationContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Administrative contact for the domain"),
    )
    tech_c = RegistrationContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Technical contact for the domain"),
    )
    billing_c = RegistrationContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("Billing contact for the domain"),
    )
    template = ZoneTemplateSerializer(
        nested=True,
        write_only=True,
        required=False,
        default=None,
        help_text=_("Template to apply to the zone"),
    )
    active = serializers.BooleanField(
        required=False,
        read_only=True,
        allow_null=True,
    )
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    def create(self, validated_data):
        template = validated_data.pop("template", None)
        nameservers = validated_data.pop("nameservers", None)

        zone = super().create(validated_data)

        if nameservers is not None:
            zone.nameservers.set(nameservers)

        if template is not None:
            template.apply_to_zone(zone)

        return zone

    def update(self, instance, validated_data):
        template = validated_data.pop("template", None)
        nameservers = validated_data.pop("nameservers", None)

        zone = super().update(instance, validated_data)

        if nameservers is not None:
            zone.nameservers.set(nameservers)

        if template is not None:
            template.apply_to_zone(zone)

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
            "template",
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
