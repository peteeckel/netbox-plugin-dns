from netbox.views import generic

from utilities.views import ViewTab, register_model_view

from netbox_dns.models import Registrar, Zone
from netbox_dns.filters import RegistrarFilter, ZoneFilter
from netbox_dns.forms import (
    RegistrarForm,
    RegistrarFilterForm,
    RegistrarImportForm,
    RegistrarBulkEditForm,
)
from netbox_dns.tables import RegistrarTable, ZoneTable


class RegistrarView(generic.ObjectView):
    queryset = Registrar.objects.all()


class RegistrarListView(generic.ObjectListView):
    queryset = Registrar.objects.all()
    table = RegistrarTable
    filterset = RegistrarFilter
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
    filterset = RegistrarFilter
    table = RegistrarTable
    form = RegistrarBulkEditForm


class RegistrarBulkDeleteView(generic.BulkDeleteView):
    queryset = Registrar.objects.all()
    table = RegistrarTable


@register_model_view(Registrar, "zones")
class RegistrarZoneListView(generic.ObjectChildrenView):
    queryset = Registrar.objects.all().prefetch_related("zone_set")
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilter
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label="Zones",
        permission="netbox_dns.view_zone",
        badge=lambda obj: obj.zone_set.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zone_set
