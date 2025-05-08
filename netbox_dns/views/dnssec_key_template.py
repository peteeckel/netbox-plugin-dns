from netbox.views import generic
from utilities.views import register_model_view

from netbox_dns.filtersets import DNSSECKeyTemplateFilterSet
from netbox_dns.forms import (
    DNSSECKeyTemplateImportForm,
    DNSSECKeyTemplateFilterForm,
    DNSSECKeyTemplateForm,
    DNSSECKeyTemplateBulkEditForm,
)
from netbox_dns.models import DNSSECKeyTemplate
from netbox_dns.tables import DNSSECKeyTemplateTable, DNSSECPolicyDisplayTable


__all__ = (
    "DNSSECKeyTemplateView",
    "DNSSECKeyTemplateListView",
    "DNSSECKeyTemplateEditView",
    "DNSSECKeyTemplateDeleteView",
    "DNSSECKeyTemplateBulkEditView",
    "DNSSECKeyTemplateBulkImportView",
    "DNSSECKeyTemplateBulkDeleteView",
)


@register_model_view(DNSSECKeyTemplate, "list", path="", detail=False)
class DNSSECKeyTemplateListView(generic.ObjectListView):
    queryset = DNSSECKeyTemplate.objects.all()
    filterset = DNSSECKeyTemplateFilterSet
    filterset_form = DNSSECKeyTemplateFilterForm
    table = DNSSECKeyTemplateTable


@register_model_view(DNSSECKeyTemplate)
class DNSSECKeyTemplateView(generic.ObjectView):
    queryset = DNSSECKeyTemplate.objects.prefetch_related("policies")

    def get_extra_context(self, request, instance):
        if instance.policies.exists():
            policy_table = DNSSECPolicyDisplayTable(data=instance.policies.all())
            policy_table.configure(request)
            return {"policy_table": policy_table}

        return {}


@register_model_view(DNSSECKeyTemplate, "add", detail=False)
@register_model_view(DNSSECKeyTemplate, "edit")
class DNSSECKeyTemplateEditView(generic.ObjectEditView):
    queryset = DNSSECKeyTemplate.objects.all()
    form = DNSSECKeyTemplateForm


@register_model_view(DNSSECKeyTemplate, "delete")
class DNSSECKeyTemplateDeleteView(generic.ObjectDeleteView):
    queryset = DNSSECKeyTemplate.objects.all()


@register_model_view(DNSSECKeyTemplate, "bulk_import", detail=False)
class DNSSECKeyTemplateBulkImportView(generic.BulkImportView):
    queryset = DNSSECKeyTemplate.objects.all()
    model_form = DNSSECKeyTemplateImportForm
    table = DNSSECKeyTemplateTable


@register_model_view(DNSSECKeyTemplate, "bulk_edit", path="edit", detail=False)
class DNSSECKeyTemplateBulkEditView(generic.BulkEditView):
    queryset = DNSSECKeyTemplate.objects.all()
    filterset = DNSSECKeyTemplateFilterSet
    table = DNSSECKeyTemplateTable
    form = DNSSECKeyTemplateBulkEditForm


@register_model_view(DNSSECKeyTemplate, "bulk_delete", path="delete", detail=False)
class DNSSECKeyTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = DNSSECKeyTemplate.objects.all()
    filterset = DNSSECKeyTemplateFilterSet
    table = DNSSECKeyTemplateTable
