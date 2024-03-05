from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import NameServer

from netbox_dns.api.nested_serializers import NestedZoneSerializer


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
    tenant = TenantSerializer(required=False, allow_null=True)

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
        brief_fields = ("id", "url", "display", "name", "description")
