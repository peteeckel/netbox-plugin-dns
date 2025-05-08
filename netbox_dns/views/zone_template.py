from netbox.views import generic
from utilities.views import register_model_view

from netbox_dns.models import ZoneTemplate
from netbox_dns.filtersets import ZoneTemplateFilterSet
from netbox_dns.forms import (
    ZoneTemplateImportForm,
    ZoneTemplateForm,
    ZoneTemplateFilterForm,
    ZoneTemplateBulkEditForm,
)
from netbox_dns.tables import ZoneTemplateTable, RecordTemplateDisplayTable


__all__ = (
    "ZoneTemplateView",
    "ZoneTemplateListView",
    "ZoneTemplateEditView",
    "ZoneTemplateDeleteView",
    "ZoneTemplateBulkImportView",
    "ZoneTemplateBulkEditView",
    "ZoneTemplateBulkDeleteView",
)


@register_model_view(ZoneTemplate, "list", path="", detail=False)
class ZoneTemplateListView(generic.ObjectListView):
    queryset = ZoneTemplate.objects.all()
    filterset = ZoneTemplateFilterSet
    filterset_form = ZoneTemplateFilterForm
    table = ZoneTemplateTable


@register_model_view(ZoneTemplate)
class ZoneTemplateView(generic.ObjectView):
    queryset = ZoneTemplate.objects.all()

    def get_extra_context(self, request, instance):
        if instance.record_templates.exists():
            record_template_table = RecordTemplateDisplayTable(
                data=instance.record_templates.all()
            )
            record_template_table.configure(request)
            return {
                "record_template_table": record_template_table,
            }

        return {}


@register_model_view(ZoneTemplate, "add", detail=False)
@register_model_view(ZoneTemplate, "edit")
class ZoneTemplateEditView(generic.ObjectEditView):
    queryset = ZoneTemplate.objects.all()
    form = ZoneTemplateForm


@register_model_view(ZoneTemplate, "delete")
class ZoneTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ZoneTemplate.objects.all()


@register_model_view(ZoneTemplate, "bulk_import", detail=False)
class ZoneTemplateBulkImportView(generic.BulkImportView):
    queryset = ZoneTemplate.objects.all()
    model_form = ZoneTemplateImportForm
    table = ZoneTemplateTable


@register_model_view(ZoneTemplate, "bulk_edit", path="edit", detail=False)
class ZoneTemplateBulkEditView(generic.BulkEditView):
    queryset = ZoneTemplate.objects.all()
    filterset = ZoneTemplateFilterSet
    table = ZoneTemplateTable
    form = ZoneTemplateBulkEditForm


@register_model_view(ZoneTemplate, "bulk_delete", path="delete", detail=False)
class ZoneTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ZoneTemplate.objects.all()
    filterset = ZoneTemplateFilterSet
    table = ZoneTemplateTable
