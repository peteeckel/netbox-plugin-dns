from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_dns.api.serializers import (
    ViewSerializer,
    ZoneSerializer,
    NameServerSerializer,
    RecordSerializer,
)
from netbox_dns.filters import ViewFilter, ZoneFilter, NameServerFilter, RecordFilter
from netbox_dns.models import View, Zone, NameServer, Record


class NetBoxDNSRootView(APIRootView):
    def get_view_name(self):
        return "NetBoxDNS"


class ViewViewSet(NetBoxModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer
    filterset_class = ViewFilter

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
    filterset_class = ZoneFilter

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
    filterset_class = NameServerFilter

    @action(detail=True, methods=["get"])
    def zones(self, request, pk=None):
        zones = Zone.objects.filter(nameservers__id=pk)
        serializer = ZoneSerializer(zones, many=True, context={"request": request})
        return Response(serializer.data)


class RecordViewSet(NetBoxModelViewSet):
    queryset = Record.objects.all().prefetch_related("zone", "zone__view", "tenant")
    serializer_class = RecordSerializer
    filterset_class = RecordFilter

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

        return super().update(request, *args, **kwargs)
