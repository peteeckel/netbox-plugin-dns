from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import register_model_view
from tenancy.views import ObjectContactsView

from netbox_dns.filtersets import DNSSECPolicyFilterSet
from netbox_dns.forms import (
    DNSSECPolicyImportForm,
    DNSSECPolicyFilterForm,
    DNSSECPolicyForm,
    DNSSECPolicyBulkEditForm,
)
from netbox_dns.models import DNSSECPolicy
from netbox_dns.tables import DNSSECPolicyTable


__all__ = (
    "DNSSECPolicyView",
    "DNSSECPolicyListView",
    "DNSSECPolicyEditView",
    "DNSSECPolicyDeleteView",
    "DNSSECPolicyBulkEditView",
    "DNSSECPolicyBulkImportView",
    "DNSSECPolicyBulkDeleteView",
)


@register_model_view(DNSSECPolicy, "list", path="", detail=False)
class DNSSECPolicyListView(generic.ObjectListView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    filterset_form = DNSSECPolicyFilterForm
    table = DNSSECPolicyTable


@register_model_view(DNSSECPolicy)
class DNSSECPolicyView(generic.ObjectView):
    queryset = DNSSECPolicy.objects.prefetch_related("key_templates")


@register_model_view(DNSSECPolicy, "add", detail=False)
@register_model_view(DNSSECPolicy, "edit")
class DNSSECPolicyEditView(generic.ObjectEditView):
    queryset = DNSSECPolicy.objects.all()
    form = DNSSECPolicyForm
    default_return_url = "plugins:netbox_dns:dnssecpolicy_list"


@register_model_view(DNSSECPolicy, "delete")
class DNSSECPolicyDeleteView(generic.ObjectDeleteView):
    queryset = DNSSECPolicy.objects.all()
    default_return_url = "plugins:netbox_dns:dnssecpolicy_list"


@register_model_view(DNSSECPolicy, "bulk_import", detail=False)
class DNSSECPolicyBulkImportView(generic.BulkImportView):
    queryset = DNSSECPolicy.objects.all()
    model_form = DNSSECPolicyImportForm
    table = DNSSECPolicyTable
    default_return_url = "plugins:netbox_dns:dnssecpolicy_list"


@register_model_view(DNSSECPolicy, "bulk_edit", path="edit", detail=False)
class DNSSECPolicyBulkEditView(generic.BulkEditView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    table = DNSSECPolicyTable
    form = DNSSECPolicyBulkEditForm


@register_model_view(DNSSECPolicy, "bulk_delete", path="delete", detail=False)
class DNSSECPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    table = DNSSECPolicyTable


@register_model_view(DNSSECPolicy, "contacts")
class DNSSECPolicyContactsView(ObjectContactsView):
    queryset = DNSSECPolicy.objects.all()
