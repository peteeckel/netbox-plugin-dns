from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_dns.models import Contact
from netbox_dns.filtersets import ContactFilterSet


class ContactType(NetBoxObjectType):
    class Meta:
        model = Contact
        fields = "__all__"
        filterset_class = ContactFilterSet


class ContactQuery(ObjectType):
    contact = ObjectField(ContactType)
    contact_list = ObjectListField(ContactType)
