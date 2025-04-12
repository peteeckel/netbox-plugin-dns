from dns import rdatatype, rdataclass

from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet
from netbox.plugins.utils import get_plugin_config

from .utilities import initialize_choice_names


__all__ = (
    "RecordTypeChoices",
    "RecordSelectableTypeChoices",
    "RecordClassChoices",
    "RecordStatusChoices",
)


def _get_config_option(option_name):
    return list(
        set(get_plugin_config("netbox_dns", option_name, []))
        | set(get_plugin_config("netbox_dns", f"{option_name}+", []))
        - set(get_plugin_config("netbox_dns", f"{option_name}-", []))
    )


class RecordTypeNames:
    def __init__(self):
        self.record_type_names = sorted(
            [
                rdtype.name
                for rdtype in rdatatype.RdataType
                if not rdatatype.is_metatype(rdtype)
            ]
            + _get_config_option("custom_record_types")
        )

    def __iter__(self):
        for rdtype_name in self.record_type_names:
            yield rdtype_name


class RecordSelectableTypeNames:
    def __init__(self, exclude_types=[]):
        self.record_type_names = sorted(
            [
                rdtype.name
                for rdtype in rdatatype.RdataType
                if not rdatatype.is_metatype(rdtype)
                and rdtype.name not in _get_config_option("filter_record_types")
            ]
            + _get_config_option("custom_record_types")
        )

    def __iter__(self):
        for rdtype_name in self.record_type_names:
            yield rdtype_name


class RecordClassNames:
    def __iter__(self):
        for rdclass in rdataclass.RdataClass:
            yield rdclass.name


@initialize_choice_names
class RecordTypeChoices(ChoiceSet):
    def choices():
        return RecordTypeNames()

    CHOICES = [(name, name) for name in choices()]

    SINGLETONS = [
        rdtype.name for rdtype in rdatatype.RdataType if rdatatype.is_singleton(rdtype)
    ]
    CUSTOM_TYPES = _get_config_option("custom_record_types")


@initialize_choice_names
class RecordSelectableTypeChoices(ChoiceSet):
    def choices():
        return RecordSelectableTypeNames()

    CHOICES = [(name, name) for name in choices()]


@initialize_choice_names
class RecordClassChoices(ChoiceSet):
    def choices():
        return RecordClassNames()

    CHOICES = [(name, name) for name in choices()]


class RecordStatusChoices(ChoiceSet):
    key = "Record.status"

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    CHOICES = [
        (STATUS_ACTIVE, _("Active"), "blue"),
        (STATUS_INACTIVE, _("Inactive"), "red"),
    ]
