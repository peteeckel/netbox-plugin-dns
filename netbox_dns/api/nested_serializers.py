from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_dns.models import View, Zone, NameServer, Record


#
# Views
#
class NestedViewSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:view-detail"
    )

    class Meta:
        model = View
        fields = ["id", "url", "display", "name"]


#
# Zones
#
class NestedZoneSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:zone-detail"
    )
    view = NestedViewSerializer(
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
        fields = ["id", "url", "display", "name", "view", "status", "active"]


#
# Nameservers
#
class NestedNameServerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:nameserver-detail"
    )

    class Meta:
        model = NameServer
        fields = ["id", "url", "display", "name"]


#
# Records
#
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
