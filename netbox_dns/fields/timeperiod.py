from django.forms import Field
from django.utils.dateparse import parse_duration
from django.core.exceptions import ValidationError

from netbox_dns.utilities import iso8601_to_int

__all__ = ("TimePeriodField",)


class TimePeriodField(Field):
    def to_python(self, value):
        if not value:
            return None

        try:
            return iso8601_to_int(value)
        except TypeError:
            raise ValidationError(
                "Enter a valid integer or ISO 8601 duration (W, M and Y are not supported)"
            )

    def validate(self, value):
        super().validate(value)

        if value is not None and value < 0:
            raise ValidationError("A time period cannot be negative.")
