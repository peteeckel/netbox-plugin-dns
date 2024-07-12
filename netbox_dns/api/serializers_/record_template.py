from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer

from netbox_dns.models import RecordTemplate


__ALL__ = ("RecordTemplateSerializer",)


class RecordTemplateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:recordtemplate-detail"
    )
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

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
