from dns import name as dns_name

from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from tenancy.views import ObjectContactsView

from netbox_dns.filtersets import NameServerFilterSet, ZoneFilterSet
from netbox_dns.forms import (
    NameServerImportForm,
    NameServerFilterForm,
    NameServerForm,
    NameServerBulkEditForm,
)
from netbox_dns.models import Zone, NameServer
from netbox_dns.tables import NameServerTable, ZoneTable


__all__ = (
    "NameServerView",
    "NameServerListView",
    "NameServerEditView",
    "NameServerDeleteView",
    "NameServerBulkEditView",
    "NameServerBulkImportView",
    "NameServerBulkDeleteView",
)


class NameServerListView(generic.ObjectListView):
    queryset = NameServer.objects.all()
    filterset = NameServerFilterSet
    filterset_form = NameServerFilterForm
    table = NameServerTable


class NameServerView(generic.ObjectView):
    queryset = NameServer.objects.all().prefetch_related("zones")

    def get_extra_context(self, request, instance):
        name = dns_name.from_text(instance.name)
        if name.to_text() != name.to_unicode():
            return {
                "unicode_name": name.to_unicode(),
            }

        return {}


class NameServerEditView(generic.ObjectEditView):
    queryset = NameServer.objects.all()
    form = NameServerForm
    default_return_url = "plugins:netbox_dns:nameserver_list"


class NameServerDeleteView(generic.ObjectDeleteView):
    queryset = NameServer.objects.all()
    default_return_url = "plugins:netbox_dns:nameserver_list"


class NameServerBulkImportView(generic.BulkImportView):
    queryset = NameServer.objects.all()
    model_form = NameServerImportForm
    table = NameServerTable
    default_return_url = "plugins:netbox_dns:nameserver_list"


class NameServerBulkEditView(generic.BulkEditView):
    queryset = NameServer.objects.all()
    filterset = NameServerFilterSet
    table = NameServerTable
    form = NameServerBulkEditForm


class NameServerBulkDeleteView(generic.BulkDeleteView):
    queryset = NameServer.objects.all()
    table = NameServerTable


@register_model_view(NameServer, "contacts")
class NameServerContactsView(ObjectContactsView):
    queryset = NameServer.objects.all()


@register_model_view(NameServer, "zones")
class NameServerZoneListView(generic.ObjectChildrenView):
    queryset = NameServer.objects.all().prefetch_related("zones")
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


@register_model_view(NameServer, "soa_zones")
class NameServerSOAZoneListView(generic.ObjectChildrenView):
    queryset = NameServer.objects.all().prefetch_related("zones_soa")
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilterSet
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("SOA Zones"),
        permission="netbox_dns.view_zone",
        badge=lambda obj: obj.zones_soa.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zones_soa
