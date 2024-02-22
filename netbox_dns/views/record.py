from dns import name as dns_name

from django.db.models import Q
from django.db.models.functions import Length

from netbox.views import generic

from netbox_dns.filtersets import RecordFilterSet
from netbox_dns.forms import (
    RecordImportForm,
    RecordFilterForm,
    RecordForm,
    RecordBulkEditForm,
)
from netbox_dns.models import Record, RecordTypeChoices, Zone
from netbox_dns.tables import RecordTable, ManagedRecordTable, RelatedRecordTable
from netbox_dns.utilities import value_to_unicode


class RecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=False).prefetch_related(
        "zone", "ptr_record"
    )
    filterset = RecordFilterSet
    filterset_form = RecordFilterForm
    table = RecordTable


class ManagedRecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=True).prefetch_related(
        "zone", "address_record"
    )
    filterset = RecordFilterSet
    filterset_form = RecordFilterForm
    table = ManagedRecordTable
    actions = {"export": {"view"}}
    template_name = "netbox_dns/record/managed.html"


class RecordView(generic.ObjectView):
    queryset = Record.objects.all().prefetch_related("zone", "ptr_record")

    def get_value_records(self, instance):
        value_fqdn = dns_name.from_text(instance.value_fqdn)
        value_zone_names = [
            value_fqdn.split(length)[1].to_text().rstrip(".")
            for length in range(2, len(value_fqdn) + 1)
        ]

        value_zone = (
            Zone.objects.filter(instance.zone.view_filter, name__in=value_zone_names)
            .order_by(Length("name").desc())
            .first()
        )
        if not value_zone:
            return None

        value_name = value_fqdn.relativize(dns_name.from_text(value_zone.name))
        cname_targets = Record.objects.filter(zone=value_zone, name=value_name)

        if cname_targets:
            return RelatedRecordTable(
                data=cname_targets,
            )

        return None

    def get_cname_records(self, instance):
        view_filter = (
            Q(zone__view__isnull=True)
            if instance.zone.view is None
            else Q(zone__view=instance.zone.view)
        )
        cname_records = set(
            Record.objects.filter(
                view_filter, value=instance.fqdn, type=RecordTypeChoices.CNAME
            )
        )

        fqdn = dns_name.from_text(instance.fqdn)
        parent_zone_names = [
            fqdn.split(length)[1].to_text().rstrip(".")
            for length in range(1, len(fqdn) + 1)
        ]

        parent_zones = Zone.objects.filter(
            instance.zone.view_filter, name__in=parent_zone_names
        )

        for parent_zone in parent_zones:
            parent_cname_records = Record.objects.filter(
                view_filter, type=RecordTypeChoices.CNAME, zone=parent_zone
            )
            cname_records = cname_records.union(
                set(
                    record
                    for record in parent_cname_records
                    if record.value_fqdn == instance.fqdn
                )
            )

        if cname_records:
            return RelatedRecordTable(
                data=cname_records,
            )

        return None

    def get_extra_context(self, request, instance):
        context = {}

        name = dns_name.from_text(instance.name, origin=None)
        if name.to_text() != name.to_unicode():
            context["unicode_name"] = name.to_unicode()

        unicode_value = value_to_unicode(instance.value)
        if instance.value != unicode_value:
            context["unicode_value"] = unicode_value

        if instance.type == RecordTypeChoices.CNAME:
            context["cname_target_table"] = self.get_value_records(instance)
        else:
            context["cname_table"] = self.get_cname_records(instance)

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
    filterset = RecordFilterSet
    table = RecordTable
    form = RecordBulkEditForm


class RecordBulkDeleteView(generic.BulkDeleteView):
    queryset = Record.objects.filter(managed=False)
    table = RecordTable
