from dns import rdatatype, rdataclass

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from netbox.plugins.utils import get_plugin_config
from utilities.choices import ChoiceSet


__all__ = (
    "RecordTypeChoices",
    "RecordSelectableTypeChoices",
    "RecordClassChoices",
    "RecordStatusChoices",
)


def define_choice_attributes(filter_name=None):
    try:
        if filter_name is not None:
            filter_choices = get_plugin_config("netbox_dns", filter_name, [])
        else:
            filter_choices = []
    except ImproperlyConfigured:
        filter_choices = []

    def decorator(cls):
        choices = []
        for choice in cls._choices:
            if choice[0] not in filter_choices:
                setattr(cls, choice[0], choice[0])
                choices.append(choice)
        cls._choices = choices
        cls.CHOICES = choices

        return cls

    return decorator


@define_choice_attributes()
class RecordTypeChoices(ChoiceSet):
    CHOICES = [
        (rdtype.name, rdtype.name)
        for rdtype in sorted(rdatatype.RdataType, key=lambda a: a.name)
        if not rdatatype.is_metatype(rdtype)
    ]
    SINGLETONS = [
        rdtype.name for rdtype in rdatatype.RdataType if rdatatype.is_singleton(rdtype)
    ]


@define_choice_attributes(filter_name="filter_record_types")
class RecordSelectableTypeChoices(ChoiceSet):
    CHOICES = [
        (rdtype.name, rdtype.name)
        for rdtype in sorted(rdatatype.RdataType, key=lambda a: a.name)
        if not rdatatype.is_metatype(rdtype)
    ]


@define_choice_attributes()
class RecordClassChoices(ChoiceSet):
    CHOICES = [
        (rdclass.name, rdclass.name)
        for rdclass in sorted(rdataclass.RdataClass)
        if not rdataclass.is_metaclass(rdclass)
    ]


class RecordStatusChoices(ChoiceSet):
    key = "Record.status"

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    CHOICES = [
        (STATUS_ACTIVE, _("Active"), "blue"),
        (STATUS_INACTIVE, _("Inactive"), "red"),
    ]
