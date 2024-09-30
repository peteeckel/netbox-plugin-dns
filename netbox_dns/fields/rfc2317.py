from netaddr import IPNetwork, AddrFormatError

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox_dns.validators import validate_ipv4, validate_prefix, validate_rfc2317
from .network import NetContains, NetContained, NetOverlap, NetMaskLength

INVALID_RFC2317 = _(
    "RFC2317 requires an IPv4 prefix with a length of at least 25 bits."
)


__all__ = (
    "RFC2317NetworkField",
    "RFC2317NetworkFormField",
)


class RFC2317NetworkFormField(forms.Field):
    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPNetwork):
            if value.version == 4 and value.prefixlen > 24:
                return value

            raise ValidationError(INVALID_RFC2317)

        if len(value.split("/")) != 2:
            raise ValidationError(_("Please specify the prefix length"))

        try:
            ip_network = IPNetwork(value)
        except AddrFormatError as exc:
            raise ValidationError(exc)

        if ip_network.version != 4 or ip_network.prefixlen <= 24:
            raise ValidationError(INVALID_RFC2317)

        return ip_network


class RFC2317NetworkField(models.Field):
    description = _("PostgreSQL CIDR field for an RFC2317 prefix")

    default_validators = [validate_ipv4, validate_prefix, validate_rfc2317]

    def python_type(self):
        return IPNetwork

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return value

        try:
            ip_network = IPNetwork(value)
        except (AddrFormatError, TypeError, ValueError) as exc:
            raise ValidationError(exc)

        if ip_network.version != 4:
            raise ValidationError(INVALID_RFC2317)

        return ip_network

    def get_prep_value(self, value):
        if not value:
            return None

        if isinstance(value, list):
            return [str(self.to_python(v)) for v in value]

        return str(self.to_python(value))

    def form_class(self):
        return RFC2317NetworkFormField

    def formfield(self, **kwargs):
        defaults = {"form_class": self.form_class()}
        defaults.update(kwargs)

        return super().formfield(**defaults)

    def db_type(self, connection):
        return "cidr"


RFC2317NetworkField.register_lookup(NetContains)
RFC2317NetworkField.register_lookup(NetContained)
RFC2317NetworkField.register_lookup(NetOverlap)
RFC2317NetworkField.register_lookup(NetMaskLength)
