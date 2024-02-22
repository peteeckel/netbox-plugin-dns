from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_dns.models import Zone
from netbox_dns.filtersets import ZoneFilterSet


class ZoneType(NetBoxObjectType):
    class Meta:
        model = Zone
        fields = "__all__"
        filterset_class = ZoneFilterSet


class ZoneQuery(ObjectType):
    zone = ObjectField(ZoneType)
    zone_list = ObjectListField(ZoneType)
