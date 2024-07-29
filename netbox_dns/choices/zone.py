from utilities.choices import ChoiceSet


__all__ = ("ZoneStatusChoices",)


class ZoneStatusChoices(ChoiceSet):
    key = "Zone.status"

    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"
    STATUS_PARKED = "parked"

    CHOICES = [
        (STATUS_ACTIVE, "Active", "blue"),
        (STATUS_RESERVED, "Reserved", "cyan"),
        (STATUS_DEPRECATED, "Deprecated", "red"),
        (STATUS_PARKED, "Parked", "gray"),
    ]
