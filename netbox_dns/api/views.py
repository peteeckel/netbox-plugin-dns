from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from ipam.models import Prefix

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_dns.api.serializers import (
    ViewSerializer,
    ZoneSerializer,
    NameServerSerializer,
    RecordSerializer,
    RegistrarSerializer,
    ContactSerializer,
    ZoneTemplateSerializer,
    RecordTemplateSerializer,
    PrefixSerializer,
)
from netbox_dns.filtersets import (
    ViewFilterSet,
    ZoneFilterSet,
    NameServerFilterSet,
    RecordFilterSet,
    RegistrarFilterSet,
    ContactFilterSet,
    ZoneTemplateFilterSet,
    RecordTemplateFilterSet,
)
from netbox_dns.models import (
    View,
    Zone,
    NameServer,
    Record,
    Registrar,
    Contact,
    ZoneTemplate,
    RecordTemplate,
)


class NetBoxDNSRootView(APIRootView):
    def get_view_name(self):
        return "NetBoxDNS"


class ViewViewSet(NetBoxModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer
    filterset_class = ViewFilterSet

    @action(detail=True, methods=["get"])
    def views(self, request, pk=None):
        views = View.objects.filter(zone=pk)
        serializer = ViewSerializer(views, many=True, context={"request": request})
        return Response(serializer.data)


class ZoneViewSet(NetBoxModelViewSet):
    queryset = Zone.objects.prefetch_related(
        "view",
        "nameservers",
        "tags",
        "soa_mname",
        "record_set",
        "tenant",
    )
    serializer_class = ZoneSerializer
    filterset_class = ZoneFilterSet

    @action(detail=True, methods=["get"])
    def records(self, request, pk=None):
        records = Record.objects.filter(zone=pk)
        serializer = RecordSerializer(records, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def nameservers(self, request, pk=None):
        nameservers = NameServer.objects.filter(zones__id=pk)
        serializer = NameServerSerializer(
            nameservers, many=True, context={"request": request}
        )
        return Response(serializer.data)


class NameServerViewSet(NetBoxModelViewSet):
    queryset = NameServer.objects.prefetch_related("zones", "tenant")
    serializer_class = NameServerSerializer
    filterset_class = NameServerFilterSet

    @action(detail=True, methods=["get"])
    def zones(self, request, pk=None):
        zones = Zone.objects.filter(nameservers__id=pk)
        serializer = ZoneSerializer(zones, many=True, context={"request": request})
        return Response(serializer.data)


class RecordViewSet(NetBoxModelViewSet):
    queryset = Record.objects.all().prefetch_related("zone", "zone__view", "tenant")
    serializer_class = RecordSerializer
    filterset_class = RecordFilterSet

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            data = [data]

        if any(record.get("managed") for record in data):
            raise serializers.ValidationError("'managed' is True, refusing create")

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        v_object = self.get_object()
        if v_object.managed:
            raise serializers.ValidationError(
                f"{v_object} is managed, refusing deletion"
            )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        v_object = self.get_object()
        if v_object.managed:
            raise serializers.ValidationError(f"{v_object} is managed, refusing update")

        if request.data.get("managed"):
            raise serializers.ValidationError(
                f"{v_object} is unmanaged, refusing update to managed"
            )

        return super().update(request, *args, **kwargs)


class RegistrarViewSet(NetBoxModelViewSet):
    queryset = Registrar.objects.all()
    serializer_class = RegistrarSerializer
    filterset_class = RegistrarFilterSet


class ContactViewSet(NetBoxModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filterset_class = ContactFilterSet


class ZoneTemplateViewSet(NetBoxModelViewSet):
    queryset = ZoneTemplate.objects.all()
    serializer_class = ZoneTemplateSerializer
    filterset_class = ZoneTemplateFilterSet


class RecordTemplateViewSet(NetBoxModelViewSet):
    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filterset_class = RecordTemplateFilterSet


class PrefixViewSet(NetBoxModelViewSet):
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer
