from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_dns.models import Registrar
from netbox_dns.filters import RegistrarFilter


class RegistrarType(NetBoxObjectType):
    class Meta:
        model = Registrar
        fields = "__all__"
        filterset_class = RegistrarFilter


class RegistrarQuery(ObjectType):
    registrar = ObjectField(RegistrarType)
    registrar_list = ObjectListField(RegistrarType)
