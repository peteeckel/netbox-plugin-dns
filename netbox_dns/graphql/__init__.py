import graphene
from graphene_django.converter import convert_django_field

from netbox_dns.fields import NetworkField, AddressField, RFC2317NetworkField


@convert_django_field.register(NetworkField)
def convert_field_to_string(field, registry=None):
    return graphene.String(description=field.help_text, required=not field.null)


@convert_django_field.register(AddressField)
def convert_field_to_string(field, registry=None):
    return graphene.String(description=field.help_text, required=not field.null)


@convert_django_field.register(RFC2317NetworkField)
def convert_field_to_string(field, registry=None):
    return graphene.String(description=field.help_text, required=not field.null)


from .schema import *

from .view import *
from .zone import *
from .nameserver import *
from .record import *
