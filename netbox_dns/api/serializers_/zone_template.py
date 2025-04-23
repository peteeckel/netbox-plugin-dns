from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import ZoneTemplate
from netbox_dns.api.nested_serializers import NestedRecordTemplateSerializer

from .nameserver import NameServerSerializer
from .registrar import RegistrarSerializer
from .registration_contact import RegistrationContactSerializer
from .dnssec_policy import DNSSECPolicySerializer


__all__ = ("ZoneTemplateSerializer",)


class ZoneTemplateSerializer(NetBoxModelSerializer):
    class Meta:
        model = ZoneTemplate

        fields = (
            "id",
            "url",
            "name",
            "description",
            "display",
            "nameservers",
            "soa_mname",
            "soa_rname",
            "dnssec_policy",
            "registrar",
            "registrant",
            "tech_c",
            "admin_c",
            "billing_c",
            "active",
            "tags",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
            "record_templates",
        )

        brief_fields = (
            "id",
            "url",
            "name",
            "display",
            "description",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zonetemplate-detail"
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
    record_templates = NestedRecordTemplateSerializer(
        many=True,
        read_only=False,
        required=False,
        help_text=_("Record templates assigned to the zone template"),
    )
    dnssec_policy = DNSSECPolicySerializer(
        nested=True,
        many=False,
        read_only=False,
        required=False,
        help_text=_("DNSSEC policy assigned to the zone template"),
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
    active = serializers.BooleanField(
        required=False,
        read_only=True,
        allow_null=True,
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )

    def create(self, validated_data):
        nameservers = validated_data.pop("nameservers", None)
        record_templates = validated_data.pop("record_templates", None)

        zone_template = super().create(validated_data)

        if nameservers is not None:
            zone_template.nameservers.set(nameservers)
        if record_templates is not None:
            zone_template.record_templates.set(record_templates)

        return zone_template

    def update(self, instance, validated_data):
        nameservers = validated_data.pop("nameservers", None)
        record_templates = validated_data.pop("record_templates", None)

        zone_template = super().update(instance, validated_data)

        if nameservers is not None:
            zone_template.nameservers.set(nameservers)
        if record_templates is not None:
            zone_template.record_templates.set(record_templates)

        return zone_template
