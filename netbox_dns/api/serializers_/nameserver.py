from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer

from netbox_dns.models import NameServer

from ..nested_serializers import NestedZoneSerializer


__all__ = ("NameServerSerializer",)


class NameServerSerializer(NetBoxModelSerializer):
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

        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:nameserver-detail"
    )
    zones = NestedZoneSerializer(
        many=True,
        read_only=True,
        required=False,
        default=None,
        help_text=_("Zones served by the authoritative nameserver"),
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )
