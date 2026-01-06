from django.forms import TextInput, IntegerField
from django.core.exceptions import ValidationError

from netbox_dns.utilities import iso8601_to_int

__all__ = ("TimePeriodField",)


class TimePeriodField(IntegerField):
    widget = TextInput

    def __init__(self, *args, **kwargs):
        placeholder = kwargs.pop("placeholder", None)

        if placeholder is not None:
            self.widget.placeholder = placeholder

        return super().__init__(*args, **kwargs)

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
