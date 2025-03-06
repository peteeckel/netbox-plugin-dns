from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import DNSSECKeyTemplate


__all__ = ("DNSSECKeyTemplateSerializer",)


class DNSSECKeyTemplateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:dnsseckeytemplate-detail"
    )
    tenant = TenantSerializer(required=False, allow_null=True)

    class Meta:
        model = DNSSECKeyTemplate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "tags",
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
        )
        brief_fields = ("id", "url", "display", "name", "description")
