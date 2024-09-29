from netbox.views import generic

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


class ZoneTemplateListView(generic.ObjectListView):
    queryset = ZoneTemplate.objects.all()
    filterset = ZoneTemplateFilterSet
    filterset_form = ZoneTemplateFilterForm
    table = ZoneTemplateTable


class ZoneTemplateView(generic.ObjectView):
    queryset = ZoneTemplate.objects.all()

    def get_extra_context(self, request, instance):
        if instance.record_templates.exists():
            return {
                "record_template_table": RecordTemplateDisplayTable(
                    data=instance.record_templates.all()
                )
            }

        return {}


class ZoneTemplateEditView(generic.ObjectEditView):
    queryset = ZoneTemplate.objects.all()
    form = ZoneTemplateForm
    default_return_url = "plugins:netbox_dns:zonetemplate_list"


class ZoneTemplateDeleteView(generic.ObjectDeleteView):
    queryset = ZoneTemplate.objects.all()
    default_return_url = "plugins:netbox_dns:zonetemplate_list"


class ZoneTemplateBulkImportView(generic.BulkImportView):
    queryset = ZoneTemplate.objects.all()
    model_form = ZoneTemplateImportForm
    table = ZoneTemplateTable
    default_return_url = "plugins:netbox_dns:zonetemplate_list"


class ZoneTemplateBulkEditView(generic.BulkEditView):
    queryset = ZoneTemplate.objects.all()
    filterset = ZoneTemplateFilterSet
    table = ZoneTemplateTable
    form = ZoneTemplateBulkEditForm
    default_return_url = "plugins:netbox_dns:zonetemplate_list"


class ZoneTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = ZoneTemplate.objects.all()
    table = ZoneTemplateTable
