from django import forms
from django.db import models
from django.db.models import Lookup, Transform, IntegerField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netaddr import AddrFormatError, IPNetwork


__all__ = ("NetworkField",)


class NetContains(Lookup):
    lookup_name = "net_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} >> {rhs}", params


class NetContainsOrEquals(Lookup):
    lookup_name = "net_contains_or_equals"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} >>= {rhs}", params


class NetContained(Lookup):
    lookup_name = "net_contained"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} << {rhs}", params


class NetContainedOrEqual(Lookup):
    lookup_name = "net_contained_or_equal"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} <<= {rhs}", params


class NetOverlap(Lookup):
    lookup_name = "net_overlap"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"{lhs} && {rhs}", params


class NetworkFormField(forms.Field):
    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, IPNetwork):
            return value

        try:
            ip_network = IPNetwork(value)
        except AddrFormatError as exc:
            raise ValidationError(exc)

        return ip_network


class NetworkField(models.Field):
    description = _("IPv4/v6 network associated with a reverse lookup zone")

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

        return ip_network

    def get_prep_value(self, value):
        if not value:
            return None

        if isinstance(value, list):
            return [str(self.to_python(v)) for v in value]

        return str(self.to_python(value))

    def form_class(self):
        return NetworkFormField

    def formfield(self, **kwargs):
        defaults = {"form_class": self.form_class()}
        defaults.update(kwargs)

        return super().formfield(**defaults)

    def db_type(self, connection):
        return "cidr"


class NetMaskLength(Transform):
    function = "MASKLEN"
    lookup_name = "net_mask_length"

    def output_field(self):
        return IntegerField()


NetworkField.register_lookup(NetContains)
NetworkField.register_lookup(NetContained)
NetworkField.register_lookup(NetContainsOrEquals)
NetworkField.register_lookup(NetContainedOrEqual)
NetworkField.register_lookup(NetOverlap)
NetworkField.register_lookup(NetMaskLength)
