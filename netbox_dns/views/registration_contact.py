from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.views import generic

from utilities.views import ViewTab, register_model_view

from netbox_dns.models import RegistrationContact, Zone
from netbox_dns.filtersets import RegistrationContactFilterSet, ZoneFilterSet
from netbox_dns.forms import (
    RegistrationContactForm,
    RegistrationContactFilterForm,
    RegistrationContactImportForm,
    RegistrationContactBulkEditForm,
)
from netbox_dns.tables import RegistrationContactTable, ZoneTable


__all__ = (
    "RegistrationContactView",
    "RegistrationContactEditView",
    "RegistrationContactListView",
    "RegistrationContactDeleteView",
    "RegistrationContactBulkImportView",
    "RegistrationContactBulkEditView",
    "RegistrationContactBulkDeleteView",
)


class RegistrationContactView(generic.ObjectView):
    queryset = RegistrationContact.objects.all()


class RegistrationContactListView(generic.ObjectListView):
    queryset = RegistrationContact.objects.all()
    table = RegistrationContactTable
    filterset = RegistrationContactFilterSet
    filterset_form = RegistrationContactFilterForm


class RegistrationContactEditView(generic.ObjectEditView):
    queryset = RegistrationContact.objects.all()
    form = RegistrationContactForm
    default_return_url = "plugins:netbox_dns:registrationcontact_list"


class RegistrationContactDeleteView(generic.ObjectDeleteView):
    queryset = RegistrationContact.objects.all()
    default_return_url = "plugins:netbox_dns:registrationcontact_list"


class RegistrationContactBulkImportView(generic.BulkImportView):
    queryset = RegistrationContact.objects.all()
    model_form = RegistrationContactImportForm
    table = RegistrationContactTable
    default_return_url = "plugins:netbox_dns:registrationcontact_list"


class RegistrationContactBulkEditView(generic.BulkEditView):
    queryset = RegistrationContact.objects.all()
    filterset = RegistrationContactFilterSet
    table = RegistrationContactTable
    form = RegistrationContactBulkEditForm


class RegistrationContactBulkDeleteView(generic.BulkDeleteView):
    queryset = RegistrationContact.objects.all()
    table = RegistrationContactTable


@register_model_view(RegistrationContact, "zones")
class RegistrationContactZoneListView(generic.ObjectChildrenView):
    queryset = RegistrationContact.objects.all().prefetch_related(
        "zone_set", "admin_c_zones", "tech_c_zones", "billing_c_zones"
    )
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilterSet
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("Zones"),
        permission="netbox_dns.view_zone",
        badge=lambda obj: len(obj.zones),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return Zone.objects.filter(
            Q(registrant=parent)
            | Q(admin_c=parent)
            | Q(tech_c=parent)
            | Q(billing_c=parent)
        )
