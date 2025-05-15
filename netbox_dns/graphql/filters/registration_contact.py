import strawberry_django
from strawberry_django import FilterLookup

from netbox.graphql.filter_mixins import NetBoxModelFilterMixin

from netbox_dns.models import RegistrationContact


__all__ = ("NetBoxDNSRegistrationContactFilter",)


@strawberry_django.filter_type(RegistrationContact, lookups=True)
class NetBoxDNSRegistrationContactFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    contact_id: FilterLookup[str] | None = strawberry_django.filter_field()
    organization: FilterLookup[str] | None = strawberry_django.filter_field()
    street: FilterLookup[str] | None = strawberry_django.filter_field()
    city: FilterLookup[str] | None = strawberry_django.filter_field()
    state_province: FilterLookup[str] | None = strawberry_django.filter_field()
    postal_code: FilterLookup[str] | None = strawberry_django.filter_field()
    country: FilterLookup[str] | None = strawberry_django.filter_field()
    phone: FilterLookup[str] | None = strawberry_django.filter_field()
    phone_ext: FilterLookup[str] | None = strawberry_django.filter_field()
    fax: FilterLookup[str] | None = strawberry_django.filter_field()
    fax_ext: FilterLookup[str] | None = strawberry_django.filter_field()
    email: FilterLookup[str] | None = strawberry_django.filter_field()
