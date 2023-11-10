from django.db.models import Q

from netbox.views import generic

from utilities.views import ViewTab, register_model_view

from netbox_dns.models import Contact, Zone
from netbox_dns.filters import ContactFilter, ZoneFilter
from netbox_dns.forms import (
    ContactForm,
    ContactFilterForm,
    ContactImportForm,
    ContactBulkEditForm,
)
from netbox_dns.tables import ContactTable, ZoneTable


class ContactView(generic.ObjectView):
    queryset = Contact.objects.all()


class ContactListView(generic.ObjectListView):
    queryset = Contact.objects.all()
    table = ContactTable
    filterset = ContactFilter
    filterset_form = ContactFilterForm


class ContactEditView(generic.ObjectEditView):
    queryset = Contact.objects.all()
    form = ContactForm
    default_return_url = "plugins:netbox_dns:contact_list"


class ContactDeleteView(generic.ObjectDeleteView):
    queryset = Contact.objects.all()
    default_return_url = "plugins:netbox_dns:contact_list"


class ContactBulkImportView(generic.BulkImportView):
    queryset = Contact.objects.all()
    model_form = ContactImportForm
    table = ContactTable
    default_return_url = "plugins:netbox_dns:contact_list"


class ContactBulkEditView(generic.BulkEditView):
    queryset = Contact.objects.all()
    filterset = ContactFilter
    table = ContactTable
    form = ContactBulkEditForm


class ContactBulkDeleteView(generic.BulkDeleteView):
    queryset = Contact.objects.all()
    table = ContactTable


@register_model_view(Contact, "zones")
class ContactZoneListView(generic.ObjectChildrenView):
    queryset = Contact.objects.all().prefetch_related(
        "zone_set", "admin_c_zones", "tech_c_zones", "billing_c_zones"
    )
    child_model = Zone
    table = ZoneTable
    filterset = ZoneFilter
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label="Zones",
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
