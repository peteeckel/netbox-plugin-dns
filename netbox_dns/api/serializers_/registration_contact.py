from rest_framework import serializers

from netbox.api.serializers import PrimaryModelSerializer

from netbox_dns.models import RegistrationContact


__all__ = ("RegistrationContactSerializer",)


class RegistrationContactSerializer(PrimaryModelSerializer):
    class Meta:
        model = RegistrationContact

        fields = (
            "id",
            "url",
            "display",
            "display_url",
            "name",
            "description",
            "tags",
            "contact_id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
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
            "contact_id",
        )

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:registrationcontact-detail"
    )
