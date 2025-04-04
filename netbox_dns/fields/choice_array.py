from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db.models import Transform, IntegerField


class ArrayLength(Transform):
    lookup_name = "length"
    function = "cardinality"

    @property
    def output_field(self):
        return IntegerField()


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


ChoiceArrayField.register_lookup(ArrayLength)
