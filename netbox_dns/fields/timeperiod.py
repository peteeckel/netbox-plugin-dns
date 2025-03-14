from django.forms import Field, TextInput
from django.utils.dateparse import parse_duration
from django.core.exceptions import ValidationError


__all__ = ("TimePeriodField",)


class TimePeriodField(Field):
    def __init__(self, *args, **kwargs):
        placeholder = kwargs.pop("placeholder", None)

        if placeholder is not None:
            self.widget = TextInput(attrs={"placeholder": placeholder})

        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None

        try:
            return int(value)
        except ValueError:
            try:
                duration = parse_duration(value)
                if duration is None:
                    raise TypeError
                return int(duration.total_seconds())
            except TypeError:
                raise ValidationError(
                    "Enter a valid integer or ISO 8601 duration (W, M and Y are not supported)"
                )

    def validate(self, value):
        super().validate(value)

        if value is not None and value < 0:
            raise ValidationError("A time period cannot be negative.")
