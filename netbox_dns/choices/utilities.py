from django.core.exceptions import ImproperlyConfigured

from netbox.plugins.utils import get_plugin_config


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
