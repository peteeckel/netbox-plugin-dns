from django.urls import reverse
from rest_framework import status

from core.models import ObjectType
from extras.choices import CustomFieldTypeChoices
from extras.models import CustomField
from ipam.models import IPAddress

__all__ = ("CustomFieldTargetAPIMixin",)


class CustomFieldTargetAPIMixin:
    def test_custom_field_target(self):
        self.add_permissions(
            "ipam.change_ipaddress",
        )

        ip_address = IPAddress.objects.create(
            address="2001:db8::dead:beef/48",
        )

        cf = CustomField.objects.create(
            name="object_field",
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=ObjectType.objects.get_for_model(self.model),
            required=False,
        )
        cf.object_types.set([ObjectType.objects.get_for_model(IPAddress)])

        instance = self.model.objects.first()

        url = reverse("ipam-api:ipaddress-detail", kwargs={"pk": ip_address.pk})
        data = {
            "custom_fields": {
                cf.name: instance.pk,
            },
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        ip_address.refresh_from_db()
        self.assertEqual(ip_address.custom_field_data[cf.name], instance.pk)
