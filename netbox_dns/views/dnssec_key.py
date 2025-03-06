from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import register_model_view
from tenancy.views import ObjectContactsView

from netbox_dns.filtersets import DNSSECKeyFilterSet
from netbox_dns.forms import (
    DNSSECKeyImportForm,
    DNSSECKeyFilterForm,
    DNSSECKeyForm,
    DNSSECKeyBulkEditForm,
)
from netbox_dns.models import DNSSECKey
from netbox_dns.tables import DNSSECKeyTable


__all__ = (
    "DNSSECKeyView",
    "DNSSECKeyListView",
    "DNSSECKeyEditView",
    "DNSSECKeyDeleteView",
    "DNSSECKeyBulkEditView",
    "DNSSECKeyBulkImportView",
    "DNSSECKeyBulkDeleteView",
)


@register_model_view(DNSSECKey, "list", path="", detail=False)
class DNSSECKeyListView(generic.ObjectListView):
    queryset = DNSSECKey.objects.all()
    filterset = DNSSECKeyFilterSet
    filterset_form = DNSSECKeyFilterForm
    table = DNSSECKeyTable


@register_model_view(DNSSECKey)
class DNSSECKeyView(generic.ObjectView):
    queryset = DNSSECKey.objects.prefetch_related("policies")


@register_model_view(DNSSECKey, "add", detail=False)
@register_model_view(DNSSECKey, "edit")
class DNSSECKeyEditView(generic.ObjectEditView):
    queryset = DNSSECKey.objects.all()
    form = DNSSECKeyForm
    default_return_url = "plugins:netbox_dns:dnsseckey_list"


@register_model_view(DNSSECKey, "delete")
class DNSSECKeyDeleteView(generic.ObjectDeleteView):
    queryset = DNSSECKey.objects.all()
    default_return_url = "plugins:netbox_dns:dnsseckey_list"


@register_model_view(DNSSECKey, "bulk_import", detail=False)
class DNSSECKeyBulkImportView(generic.BulkImportView):
    queryset = DNSSECKey.objects.all()
    model_form = DNSSECKeyImportForm
    table = DNSSECKeyTable
    default_return_url = "plugins:netbox_dns:dnsseckey_list"


@register_model_view(DNSSECKey, "bulk_edit", path="edit", detail=False)
class DNSSECKeyBulkEditView(generic.BulkEditView):
    queryset = DNSSECKey.objects.all()
    filterset = DNSSECKeyFilterSet
    table = DNSSECKeyTable
    form = DNSSECKeyBulkEditForm


@register_model_view(DNSSECKey, "bulk_delete", path="delete", detail=False)
class DNSSECKeyBulkDeleteView(generic.BulkDeleteView):
    queryset = DNSSECKey.objects.all()
    filterset = DNSSECKeyFilterSet
    table = DNSSECKeyTable


@register_model_view(DNSSECKey, "contacts")
class DNSSECKeyContactsView(ObjectContactsView):
    queryset = DNSSECKey.objects.all()
