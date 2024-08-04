from netbox.models import NetBoxModel


__all__ = ("ObjectModificationMixin",)


class ObjectModificationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self.__class__, "check_fields"):
            self.__class__.check_fields = (
                {field.name for field in self._meta.fields}
                - {field.name for field in NetBoxModel._meta.fields}
                - {"id"}
            )

            self.__class__.check_fields.add("custom_field_data")

    @property
    def changed_fields(self):
        if self.pk is None:
            return None

        saved = self.__class__.objects.get(pk=self.pk)

        return {
            field
            for field in self.check_fields
            if getattr(self, field) != getattr(saved, field)
        }
