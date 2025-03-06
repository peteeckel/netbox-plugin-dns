from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.routers import APIRootView

from ipam.models import Prefix
from ipam.filtersets import PrefixFilterSet

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_dns.api.serializers import (
    ViewSerializer,
    ZoneSerializer,
    NameServerSerializer,
    RecordSerializer,
    RegistrarSerializer,
    RegistrationContactSerializer,
    ZoneTemplateSerializer,
    RecordTemplateSerializer,
    DNSSECKeyTemplateSerializer,
    DNSSECPolicySerializer,
    PrefixSerializer,
)
from netbox_dns.filtersets import (
    ViewFilterSet,
    ZoneFilterSet,
    NameServerFilterSet,
    RecordFilterSet,
    RegistrarFilterSet,
    RegistrationContactFilterSet,
    ZoneTemplateFilterSet,
    RecordTemplateFilterSet,
    DNSSECKeyTemplateFilterSet,
    DNSSECPolicyFilterSet,
)
from netbox_dns.models import (
    View,
    Zone,
    NameServer,
    Record,
    Registrar,
    RegistrationContact,
    ZoneTemplate,
    RecordTemplate,
    DNSSECKeyTemplate,
    DNSSECPolicy,
)


class NetBoxDNSRootView(APIRootView):
    def get_view_name(self):
        return "NetBoxDNS"


class ViewViewSet(NetBoxModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer
    filterset_class = ViewFilterSet


class ZoneViewSet(NetBoxModelViewSet):
    queryset = Zone.objects.prefetch_related(
        "view",
        "nameservers",
        "tags",
        "soa_mname",
        "records",
        "tenant",
    )
    serializer_class = ZoneSerializer
    filterset_class = ZoneFilterSet


class NameServerViewSet(NetBoxModelViewSet):
    queryset = NameServer.objects.prefetch_related("zones", "tenant")
    serializer_class = NameServerSerializer
    filterset_class = NameServerFilterSet


class RecordViewSet(NetBoxModelViewSet):
    queryset = Record.objects.prefetch_related("zone", "zone__view", "tenant")
    serializer_class = RecordSerializer
    filterset_class = RecordFilterSet

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            data = [data]

        if any(record.get("managed") for record in data):
            raise serializers.ValidationError(_("'managed' is True, refusing create"))

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        v_object = self.get_object()
        if v_object.managed:
            raise serializers.ValidationError(
                _("{object} is managed, refusing deletion").format(object=v_object)
            )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        v_object = self.get_object()
        if v_object.managed:
            raise serializers.ValidationError(
                _("{object} is managed, refusing update").format(object=v_object)
            )

        if request.data.get("managed"):
            raise serializers.ValidationError(
                _("{object} is unmanaged, refusing update to managed").format(
                    object=v_object
                )
            )

        return super().update(request, *args, **kwargs)


class RegistrarViewSet(NetBoxModelViewSet):
    queryset = Registrar.objects.all()
    serializer_class = RegistrarSerializer
    filterset_class = RegistrarFilterSet


class RegistrationContactViewSet(NetBoxModelViewSet):
    queryset = RegistrationContact.objects.all()
    serializer_class = RegistrationContactSerializer
    filterset_class = RegistrationContactFilterSet


class ZoneTemplateViewSet(NetBoxModelViewSet):
    queryset = ZoneTemplate.objects.all()
    serializer_class = ZoneTemplateSerializer
    filterset_class = ZoneTemplateFilterSet


class RecordTemplateViewSet(NetBoxModelViewSet):
    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filterset_class = RecordTemplateFilterSet


class DNSSECKeyTemplateViewSet(NetBoxModelViewSet):
    queryset = DNSSECKeyTemplate.objects.all()
    serializer_class = DNSSECKeyTemplateSerializer
    filterset_class = DNSSECKeyTemplateFilterSet


class DNSSECPolicyViewSet(NetBoxModelViewSet):
    queryset = DNSSECPolicy.objects.all()
    serializer_class = DNSSECPolicySerializer
    filterset_class = DNSSECPolicyFilterSet


class PrefixViewSet(NetBoxModelViewSet):
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer
    filterset_class = PrefixFilterSet
