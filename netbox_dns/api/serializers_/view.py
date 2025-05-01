from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from ipam.api.serializers import PrefixSerializer

from netbox_dns.models import View


__all__ = ("ViewSerializer",)


class ViewSerializer(NetBoxModelSerializer):
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
            "prefixes",
            "ip_address_filter",
        )

        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "default_view",
            "description",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:view-detail"
    )
    default_view = serializers.BooleanField(
        read_only=True,
    )
    prefixes = PrefixSerializer(
        many=True,
        nested=True,
        read_only=False,
        required=False,
        help_text=_("IPAM Prefixes assigned to the View"),
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )

    def create(self, validated_data):
        prefixes = validated_data.pop("prefixes", None)

        view = super().create(validated_data)

        if prefixes is not None:
            view.prefixes.set(prefixes)

        return view

    def update(self, instance, validated_data):
        prefixes = validated_data.pop("prefixes", None)

        view = super().update(instance, validated_data)

        if prefixes is not None:
            view.prefixes.set(prefixes)

        return view
