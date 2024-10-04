from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


__all__ = ("ZoneStatusChoices",)


class ZoneStatusChoices(ChoiceSet):
    key = "Zone.status"

    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"
    STATUS_PARKED = "parked"
    STATUS_DYNAMIC = "dynamic"

    CHOICES = [
        (STATUS_ACTIVE, _("Active"), "blue"),
        (STATUS_RESERVED, _("Reserved"), "cyan"),
        (STATUS_DEPRECATED, _("Deprecated"), "red"),
        (STATUS_PARKED, _("Parked"), "gray"),
        (STATUS_DYNAMIC, _("Dynamic"), "orange"),
    ]
