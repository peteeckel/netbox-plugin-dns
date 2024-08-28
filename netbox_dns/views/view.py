from utilities.views import ViewTab, register_model_view

from netbox.views import generic
from utilities.views import register_model_view
from tenancy.views import ObjectContactsView

from netbox_dns.models import View, Zone
from netbox_dns.filtersets import ViewFilterSet, ZoneFilterSet
from netbox_dns.forms import ViewForm, ViewFilterForm, ViewImportForm, ViewBulkEditForm
from netbox_dns.tables import ViewTable, ZoneTable


__all__ = (
    "ViewView",
    "ViewListView",
    "ViewEditView",
    "ViewDeleteView",
    "ViewBulkImportView",
    "ViewBulkEditView",
    "ViewBulkDeleteView",
    "ViewContactsView",
    "ViewZoneListView",
)


class ViewView(generic.ObjectView):
    queryset = View.objects.all().prefetch_related("zone_set")


class ViewListView(generic.ObjectListView):
    queryset = View.objects.all()
    table = ViewTable
    filterset = ViewFilterSet
    filterset_form = ViewFilterForm


class ViewEditView(generic.ObjectEditView):
    queryset = View.objects.all()
    form = ViewForm
    default_return_url = "plugins:netbox_dns:view_list"


class ViewDeleteView(generic.ObjectDeleteView):
    queryset = View.objects.all()
    default_return_url = "plugins:netbox_dns:view_list"


class ViewBulkImportView(generic.BulkImportView):
    queryset = View.objects.all()
    model_form = ViewImportForm
    table = ViewTable
    default_return_url = "plugins:netbox_dns:view_list"


class ViewBulkEditView(generic.BulkEditView):
    queryset = View.objects.all()
    filterset = ViewFilterSet
    table = ViewTable
    form = ViewBulkEditForm


class ViewBulkDeleteView(generic.BulkDeleteView):
    queryset = View.objects.all()
    table = ViewTable


@register_model_view(View, "zones")
class ViewZoneListView(generic.ObjectChildrenView):
    queryset = View.objects.all().prefetch_related("zone_set")
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilterSet
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


@register_model_view(View, "contacts")
class ViewContactsView(ObjectContactsView):
    queryset = View.objects.all()
