from django.utils.translation import gettext as _

from netbox.views import generic

from utilities.views import ViewTab, register_model_view

from netbox_dns.models import Registrar, Zone
from netbox_dns.filtersets import RegistrarFilterSet, ZoneFilterSet
from netbox_dns.forms import (
    RegistrarForm,
    RegistrarFilterForm,
    RegistrarImportForm,
    RegistrarBulkEditForm,
)
from netbox_dns.tables import RegistrarTable, ZoneTable


__all__ = (
    "RegistrarView",
    "RegistrarListView",
    "RegistrarEditView",
    "RegistrarDeleteView",
    "RegistrarBulkImportView",
    "RegistrarBulkEditView",
    "RegistrarBulkDeleteView",
)


class RegistrarView(generic.ObjectView):
    queryset = Registrar.objects.all()


class RegistrarListView(generic.ObjectListView):
    queryset = Registrar.objects.all()
    table = RegistrarTable
    filterset = RegistrarFilterSet
    filterset_form = RegistrarFilterForm


class RegistrarEditView(generic.ObjectEditView):
    queryset = Registrar.objects.all()
    form = RegistrarForm
    default_return_url = "plugins:netbox_dns:registrar_list"


class RegistrarDeleteView(generic.ObjectDeleteView):
    queryset = Registrar.objects.all()
    default_return_url = "plugins:netbox_dns:registrar_list"


class RegistrarBulkImportView(generic.BulkImportView):
    queryset = Registrar.objects.all()
    model_form = RegistrarImportForm
    table = RegistrarTable
    default_return_url = "plugins:netbox_dns:registrar_list"


class RegistrarBulkEditView(generic.BulkEditView):
    queryset = Registrar.objects.all()
    filterset = RegistrarFilterSet
    table = RegistrarTable
    form = RegistrarBulkEditForm


class RegistrarBulkDeleteView(generic.BulkDeleteView):
    queryset = Registrar.objects.all()
    table = RegistrarTable


@register_model_view(Registrar, "zones")
class RegistrarZoneListView(generic.ObjectChildrenView):
    queryset = Registrar.objects.prefetch_related("zones")
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilterSet
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("Zones"),
        permission="netbox_dns.view_zone",
        badge=lambda obj: obj.zones.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zones
