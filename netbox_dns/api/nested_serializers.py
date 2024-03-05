from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_dns.models import Zone, Record
from netbox_dns.api.serializers_.view import ViewSerializer


class NestedZoneSerializer(WritableNestedSerializer):
    def to_representation(self, instance):
        # +
        # Workaround for the problem that the serializer does not return the
        # annotation "active" when called with "many=False". See issue
        # https://github.com/peteeckel/netbox-plugin-dns/issues/132
        #
        # TODO: Investigate root cause, probably in DRF.
        # -
        representation = super().to_representation(instance)
        if representation.get("active") is None:
            representation["active"] = instance.is_active

        return representation

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    view = ViewSerializer(
        nested=True,
        many=False,
        required=False,
        read_only=True,
        help_text="View the zone belongs to",
    )
    active = serializers.BooleanField(
        required=False,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Zone
        fields = [
            "id",
            "url",
            "display",
            "name",
            "view",
            "status",
            "active",
            "rfc2317_prefix",
        ]


class NestedRecordSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:record-detail"
    )
    zone = NestedZoneSerializer(
        many=False,
        required=False,
        help_text="Zone the record belongs to",
    )
    active = serializers.BooleanField(
        required=False,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Record
        fields = [
            "id",
            "url",
            "display",
            "type",
            "name",
            "value",
            "status",
            "ttl",
            "zone",
            "active",
        ]
