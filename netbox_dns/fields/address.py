from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netaddr import AddrFormatError, IPAddress

from ipam.formfields import IPAddressFormField


__all__ = ("AddressField",)


class AddressField(models.Field):
    description = _("IPv4/v6 address")

    def python_type(self):
        return IPAddress

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value

        try:
            ip_address = IPAddress(value)
        except (AddrFormatError, TypeError, ValueError) as exc:
            raise ValidationError(exc)

        return ip_address

    def get_prep_value(self, value):
        if not value:
            return None

        if isinstance(value, list):
            return [str(self.to_python(v)) for v in value]

        return str(self.to_python(value))

    def form_class(self):
        return IPAddressFormField

    def formfield(self, **kwargs):
        defaults = {"form_class": self.form_class()}
        defaults.update(kwargs)

        return super().formfield(**defaults)

    def db_type(self, connection):
        return "inet"
