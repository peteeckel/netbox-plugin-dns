from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import DNSSECPolicy

from .dnssec_key_template import DNSSECKeyTemplateSerializer


__all__ = ("DNSSECPolicySerializer",)


class DNSSECPolicySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:dnssecpolicy-detail"
    )
    key_templates = DNSSECKeyTemplateSerializer(
        nested=True,
        many=True,
        read_only=False,
        required=False,
        default=None,
        help_text=_("Key templates assigned to the policy"),
    )
    tenant = TenantSerializer(required=False, allow_null=True)

    class Meta:
        model = DNSSECPolicy
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "tags",
            "key_templates",
            "inline_signing",
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
        )
        brief_fields = ("id", "url", "display", "name", "description")

    def create(self, validated_data):
        dnssec_key_templates = validated_data.pop("key_templates", None)

        dnssec_policy = super().create(validated_data)

        if dnssec_key_templates is not None:
            dnssec_policy.key_templates.set(dnssec_key_templates)

        return dnssec_policy

    def update(self, instance, validated_data):
        dnssec_key_templates = validated_data.pop("key_templates", None)

        dnssec_policy = super().update(instance, validated_data)

        if dnssec_key_templates is not None:
            dnssec_policy.key_templates.set(dnssec_key_templates)

        return dnssec_policy
