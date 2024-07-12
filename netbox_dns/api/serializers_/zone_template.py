from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from .nameserver import NameServerSerializer
from .registrar import RegistrarSerializer
from .contact import ContactSerializer

from netbox_dns.models import ZoneTemplate


__ALL__ = ("ZoneTemplateSerializer",)


class ZoneTemplateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zonetemplate-detail"
    )
    nameservers = NameServerSerializer(
        nested=True,
        many=True,
        read_only=False,
        required=False,
        help_text="Nameservers for the zone",
    )
    registrar = RegistrarSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text="The registrar the domain is registered with",
    )
    registrant = ContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text="The owner of the domain",
    )
    admin_c = ContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text="The administrative contact for the domain",
    )
    tech_c = ContactSerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text="The technical contact for the domain",
    )
    billing_c = ContactSerializer(
        nested=True,
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

        zone_template = super().create(validated_data)

        if nameservers is not None:
            zone_template.nameservers.set(nameservers)

        return zone_template

    def update(self, instance, validated_data):
        nameservers = validated_data.pop("nameservers", None)

        zone_template = super().update(instance, validated_data)

        if nameservers is not None:
            zone_template.nameservers.set(nameservers)

        return zone_template

    class Meta:
        model = ZoneTemplate
        fields = (
            "id",
            "url",
            "name",
            "display",
            "nameservers",
            "description",
            "tags",
            "created",
            "last_updated",
            "registrar",
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
            "display",
            "description",
        )
