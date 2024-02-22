from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_dns.models import Registrar
from netbox_dns.filtersets import RegistrarFilterSet


class RegistrarType(NetBoxObjectType):
    class Meta:
        model = Registrar
        fields = "__all__"
        filterset_class = RegistrarFilterSet


class RegistrarQuery(ObjectType):
    registrar = ObjectField(RegistrarType)
    registrar_list = ObjectListField(RegistrarType)
