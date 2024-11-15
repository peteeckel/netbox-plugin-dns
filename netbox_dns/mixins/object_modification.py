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

        self._save_field_values()

    def _save_field_values(self):
        for field in self.check_fields:
            if field == "custom_field_data":
                self._saved_custom_field_data = self.custom_field_data.copy()
                continue

            if f"{field}_id" in self.__dict__:
                setattr(self, f"_saved_{field}_id", self.__dict__.get(f"{field}_id"))
            else:
                setattr(self, f"_saved_{field}", self.__dict__.get(field))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self._save_field_values()

    @property
    def changed_fields(self):
        if self._state.adding:
            return None

        _changed_fields = set()
        for field in self.check_fields:
            if f"_saved_{field}_id" in self.__dict__:
                if self.__dict__.get(f"_saved_{field}_id") != self.__dict__.get(
                    f"{field}_id"
                ):
                    _changed_fields.add(field)
            else:
                if self.__dict__.get(f"_saved_{field}") != self.__dict__.get(field):
                    _changed_fields.add(field)

        return _changed_fields

    def get_saved_value(self, field):
        return self.__dict__.get(f"_saved_{field}")
