from dns import name as dns_name

from netbox.views import generic

from netbox_dns.filtersets import RecordTemplateFilterSet
from netbox_dns.forms import (
    RecordTemplateImportForm,
    RecordTemplateFilterForm,
    RecordTemplateForm,
    RecordTemplateBulkEditForm,
)
from netbox_dns.models import RecordTemplate
from netbox_dns.tables import RecordTemplateTable, ZoneTemplateDisplayTable
from netbox_dns.utilities import value_to_unicode


__all__ = (
    "RecordTemplateView",
    "RecordTemplateListView",
    "RecordTemplateEditView",
    "RecordTemplateDeleteView",
    "RecordTemplateBulkImportView",
    "RecordTemplateBulkEditView",
    "RecordTemplateBulkDeleteView",
)


class RecordTemplateListView(generic.ObjectListView):
    queryset = RecordTemplate.objects.all()
    filterset = RecordTemplateFilterSet
    filterset_form = RecordTemplateFilterForm
    table = RecordTemplateTable


class RecordTemplateView(generic.ObjectView):
    queryset = RecordTemplate.objects.all()

    def get_extra_context(self, request, instance):
        context = {}

        name = dns_name.from_text(instance.record_name, origin=None)
        if name.to_text() != name.to_unicode():
            context["unicode_name"] = name.to_unicode()

        unicode_value = value_to_unicode(instance.value)
        if instance.value != unicode_value:
            context["unicode_value"] = unicode_value

        if instance.zone_templates.exists():
            context["zone_template_table"] = ZoneTemplateDisplayTable(
                data=instance.zone_templates.all()
            )

        return context


class RecordTemplateEditView(generic.ObjectEditView):
    queryset = RecordTemplate.objects.all()
    form = RecordTemplateForm
    default_return_url = "plugins:netbox_dns:recordtemplate_list"


class RecordTemplateDeleteView(generic.ObjectDeleteView):
    queryset = RecordTemplate.objects.all()
    default_return_url = "plugins:netbox_dns:recordtemplate_list"


class RecordTemplateBulkImportView(generic.BulkImportView):
    queryset = RecordTemplate.objects.all()
    model_form = RecordTemplateImportForm
    table = RecordTemplateTable
    default_return_url = "plugins:netbox_dns:recordtemplate_list"


class RecordTemplateBulkEditView(generic.BulkEditView):
    queryset = RecordTemplate.objects.all()
    filterset = RecordTemplateFilterSet
    table = RecordTemplateTable
    form = RecordTemplateBulkEditForm


class RecordTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = RecordTemplate.objects.all()
    table = RecordTemplateTable
