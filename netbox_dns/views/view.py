from utilities.views import ViewTab, register_model_view
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from tenancy.views import ObjectContactsView
from ipam.models import Prefix

from netbox_dns.models import View, Zone
from netbox_dns.filtersets import ViewFilterSet, ZoneFilterSet
from netbox_dns.forms import (
    ViewForm,
    ViewFilterForm,
    ViewImportForm,
    ViewBulkEditForm,
    ViewPrefixEditForm,
)
from netbox_dns.tables import ViewTable, ZoneTable
from netbox_dns.utilities import get_views_by_prefix


__all__ = (
    "ViewView",
    "ViewListView",
    "ViewEditView",
    "ViewDeleteView",
    "ViewBulkImportView",
    "ViewBulkEditView",
    "ViewBulkDeleteView",
    "ViewPrefixEditView",
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


class ViewPrefixEditView(generic.ObjectEditView):
    queryset = Prefix.objects.all()
    form = ViewPrefixEditForm
    template_name = "netbox_dns/view/prefix.html"

    def get_extra_context(self, request, instance):
        parents = instance.get_parents()
        if parents:
            return {
                "inherited_views": get_views_by_prefix(parents.last()),
                "inherited_from": parents.filter(netbox_dns_views__isnull=False).last(),
            }

        return {}


@register_model_view(View, "zones")
class ViewZoneListView(generic.ObjectChildrenView):
    queryset = View.objects.all().prefetch_related("zone_set")
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilterSet
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("Zones"),
        permission="netbox_dns.view_zone",
        badge=lambda obj: obj.zone_set.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zone_set


@register_model_view(View, "contacts")
class ViewContactsView(ObjectContactsView):
    queryset = View.objects.all()
