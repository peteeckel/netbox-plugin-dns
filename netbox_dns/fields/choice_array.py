from django import forms
from django.contrib.postgres.fields import ArrayField


class _TypedMultipleChoiceField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)

        super().__init__(*args, **kwargs)


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        return super().formfield(
            form_class=_TypedMultipleChoiceField,
            choices=self.base_field.choices,
            coerce=self.base_field.to_python,
            **kwargs,
        )
