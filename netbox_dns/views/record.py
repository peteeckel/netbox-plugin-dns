from dns import name as dns_name

from netbox.views import generic

from netbox_dns.filters import RecordFilter
from netbox_dns.forms import (
    RecordImportForm,
    RecordFilterForm,
    RecordForm,
    RecordBulkEditForm,
)
from netbox_dns.models import Record
from netbox_dns.tables import RecordTable, ManagedRecordTable
from netbox_dns.utilities import value_to_unicode


class RecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=False).prefetch_related(
        "zone", "ptr_record"
    )
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    table = RecordTable


class ManagedRecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=True).prefetch_related(
        "zone", "address_record"
    )
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    table = ManagedRecordTable
    actions = ("export",)
    template_name = "netbox_dns/record/managed.html"


class RecordView(generic.ObjectView):
    queryset = Record.objects.all().prefetch_related("zone", "ptr_record")

    def get_extra_context(self, request, instance):
        context = {}

        name = dns_name.from_text(instance.name, origin=None)
        if name.to_text() != name.to_unicode():
            context["unicode_name"] = name.to_unicode()

        unicode_value = value_to_unicode(instance.value)
        if instance.value != unicode_value:
            context["unicode_value"] = unicode_value

        return context


class RecordEditView(generic.ObjectEditView):
    queryset = Record.objects.filter(managed=False).prefetch_related(
        "zone", "ptr_record"
    )
    form = RecordForm
    default_return_url = "plugins:netbox_dns:record_list"


class RecordDeleteView(generic.ObjectDeleteView):
    queryset = Record.objects.filter(managed=False)
    default_return_url = "plugins:netbox_dns:record_list"


class RecordBulkImportView(generic.BulkImportView):
    queryset = Record.objects.filter(managed=False).prefetch_related(
        "zone", "ptr_record"
    )
    model_form = RecordImportForm
    table = RecordTable
    default_return_url = "plugins:netbox_dns:record_list"


class RecordBulkEditView(generic.BulkEditView):
    queryset = Record.objects.filter(managed=False).prefetch_related("zone")
    filterset = RecordFilter
    table = RecordTable
    form = RecordBulkEditForm


class RecordBulkDeleteView(generic.BulkDeleteView):
    queryset = Record.objects.filter(managed=False)
    table = RecordTable
