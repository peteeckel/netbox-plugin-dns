from django.utils.translation import gettext as _
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer

from netbox_dns.models import RecordTemplate

from ..nested_serializers import NestedZoneTemplateSerializer


__all__ = ("RecordTemplateSerializer",)


class RecordTemplateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:recordtemplate-detail"
    )
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    zone_templates = NestedZoneTemplateSerializer(
        many=True,
        read_only=True,
        required=False,
        help_text=_("Zone templates using the record template"),
    )

    class Meta:
        model = RecordTemplate
        fields = (
            "id",
            "url",
            "display",
            "type",
            "name",
            "record_name",
            "value",
            "status",
            "ttl",
            "description",
            "tags",
            "created",
            "last_updated",
            "disable_ptr",
            "custom_fields",
            "tenant",
            "zone_templates",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "type",
            "name",
            "record_name",
            "value",
            "status",
            "ttl",
            "description",
        )
