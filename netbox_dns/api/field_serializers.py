from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from netbox_dns.utilities import iso8601_to_int

__all__ = ("TimePeriodField",)


class TimePeriodField(serializers.IntegerField):
    default_error_messages = {
        "invalid": _(
            "Enter a positive integer or an ISO8601 duration (W, M and Y are not supported)."
        ),
    }

    def to_internal_value(self, data):
        try:
            return iso8601_to_int(data)
        except TypeError:
            raise serializers.ValidationError(
                "Enter a valid integer or ISO 8601 duration (W, M and Y are not supported)."
            )

    def to_representation(self, value):
        return value
