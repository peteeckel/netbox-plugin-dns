from dns import name as dns_name

from netbox.views import generic

from netbox_dns.filtersets import ZoneTemplateFilterSet
from netbox_dns.forms import (
    ZoneTemplateImportForm,
    ZoneTemplateForm,
    ZoneTemplateFilterForm,
    ZoneTemplateBulkEditForm,
)
from netbox_dns.models import ZoneTemplate
from netbox_dns.tables import ZoneTemplateTable


__ALL__ = (
    "ZoneTemplateListView",
    "ZoneTemplateView",
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