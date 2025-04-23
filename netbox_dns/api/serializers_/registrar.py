from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from netbox_dns.models import Registrar


__all__ = ("RegistrarSerializer",)


class RegistrarSerializer(NetBoxModelSerializer):
    class Meta:
        model = Registrar

        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "iana_id",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
            "created",
            "last_updated",
            "custom_fields",
        )

        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "iana_id",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:registrar-detail"
    )
