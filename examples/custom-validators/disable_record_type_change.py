# +
# Do not allow the type of a record to be changed.
#
# This does not affect record creation, but after a record has been created
# and saved changing the record type is not allowed.
# -

from extras.validators import CustomValidator


class TypeChangeValidator(CustomValidator):
    def validate(self, record, request):
        if record._state.adding:
            return

        saved_type = record._meta.model.objects.get(pk=record.pk).type
        if record.type != saved_type:
            self.fail("The record type must not be changed", field="type")
