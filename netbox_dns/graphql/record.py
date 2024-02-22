from graphene import ObjectType

from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from netbox_dns.models import Record
from netbox_dns.filtersets import RecordFilterSet


class RecordType(NetBoxObjectType):
    class Meta:
        model = Record
        fields = "__all__"
        filterset_class = RecordFilterSet


class RecordQuery(ObjectType):
    record = ObjectField(RecordType)
    record_list = ObjectListField(RecordType)
