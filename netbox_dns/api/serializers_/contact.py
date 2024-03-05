from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from netbox_dns.models import Contact


class ContactSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_dns-api:contact-detail"
    )

    class Meta:
        model = Contact
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
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
        brief_fields = ("id", "url", "display", "name", "description", "contact_id")
