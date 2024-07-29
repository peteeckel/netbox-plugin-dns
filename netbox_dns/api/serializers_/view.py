from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import View


__all__ = ("ViewSerializer",)


class ViewSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:view-detail"
    )
    default_view = serializers.BooleanField(
        read_only=True,
    )

    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = View
        fields = (
            "id",
            "url",
            "display",
            "name",
            "default_view",
            "tags",
            "description",
            "created",
            "last_updated",
            "custom_fields",
            "tenant",
        )
        brief_fields = ("id", "url", "display", "name", "default_view", "description")
