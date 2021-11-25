from netbox.views import generic
from netbox_dns.filters import NameServerFilter, RecordFilter, ZoneFilter
from netbox_dns.forms import (
    NameServerCSVForm,
    NameServerFilterForm,
    NameServerForm,
    RecordCSVForm,
    RecordFilterForm,
    RecordForm,
    RecordBulkEditForm,
    ZoneCSVForm,
    ZoneForm,
    ZoneFilterForm,
    ZoneBulkEditForm,
)
from netbox_dns.models import Record, Zone, NameServer
from netbox_dns.tables import (
    NameServerTable,
    RecordTable,
    ManagedRecordTable,
    ZoneTable,
    ZoneManagedRecordTable,
    ZoneRecordTable,
)
from utilities.tables import paginate_table


#
# Zone
#


class ZoneListView(generic.ObjectListView):
    """View for listing all existing Zones."""

    queryset = Zone.objects.all()
    filterset = ZoneFilter
    filterset_form = ZoneFilterForm
    table = ZoneTable
    template_name = "netbox_dns/object_list.html"


class ZoneView(generic.ObjectView):
    """Display Zone details"""

    queryset = Zone.objects.all()

    def get_extra_context(self, request, instance):
        nameserver_warnings = instance.check_nameservers()

        return {
            "nameserver_warnings": nameserver_warnings,
        }


class ZoneEditView(generic.ObjectEditView):
    """View for editing and creating a Zone instance."""

    queryset = Zone.objects.all()
    model_form = ZoneForm


class ZoneDeleteView(generic.ObjectDeleteView):
    """View for deleting a Zone instance"""

    queryset = Zone.objects.all()


class ZoneBulkImportView(generic.BulkImportView):
    queryset = Zone.objects.all()
    model_form = ZoneCSVForm
    table = ZoneTable


class ZoneBulkEditView(generic.BulkEditView):
    queryset = Zone.objects.all()
    filterset = ZoneFilter
    table = ZoneTable
    form = ZoneBulkEditForm


class ZoneBulkDeleteView(generic.BulkDeleteView):
    queryset = Zone.objects.all()
    table = ZoneTable


class ZoneRecordListView(generic.ObjectView):
    queryset = Zone.objects.all()
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    template_name = "netbox_dns/zone_record.html"

    def get_extra_context(self, request, instance):
        zone_records = Record.objects.filter(managed=False, zone_id=instance.pk)

        table = ZoneRecordTable(list(zone_records), user=request.user)
        if request.user.has_perm("netbox_dns.change_record") or request.user.has_perm(
            "netbox_dns.delete_record"
        ):
            table.columns.show("pk")
        paginate_table(table, request)

        permissions = {
            "change": request.user.has_perm("netbox_dns.change_record"),
            "delete": request.user.has_perm("netbox_dns.delete_record"),
        }
        bulk_querystring = f"zone_id={instance.pk}"

        return {
            "active_tab": "record_list",
            "table": table,
            "permissions": permissions,
            "bulk_querystring": bulk_querystring,
        }


class ZoneManagedRecordListView(generic.ObjectView):
    queryset = Zone.objects.all()
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    template_name = "netbox_dns/zone_managed_record.html"

    def get_extra_context(self, request, instance):
        zone_records = Record.objects.filter(managed=True, zone_id=instance.pk)

        table = ZoneManagedRecordTable(list(zone_records), user=request.user)
        paginate_table(table, request)

        return {
            "active_tab": "managed_record_list",
            "table": table,
        }


#
# NameServer
#


class NameServerListView(generic.ObjectListView):
    queryset = NameServer.objects.all()
    filterset = NameServerFilter
    filterset_form = NameServerFilterForm
    table = NameServerTable
    template_name = "netbox_dns/object_list.html"


class NameServerView(generic.ObjectView):
    """Display NameServer details"""

    queryset = NameServer.objects.all()

    def get_extra_context(self, request, instance):
        zones = instance.zones.all()
        zone_table = ZoneTable(list(zones), user=request.user)

        change_zone = request.user.has_perm("netbox_dns.change_zone")
        delete_zone = request.user.has_perm("netbox_dns.delete_zone")

        if change_zone or delete_zone:
            zone_table.columns.show("pk")
        paginate_table(zone_table, request)

        return {
            "zone_table": zone_table,
            "permissions": {
                "change": change_zone,
                "delete": delete_zone,
            },
            "model": Zone,
        }


class NameServerEditView(generic.ObjectEditView):
    """View for editing a Name Server instance."""

    queryset = NameServer.objects.all()
    model_form = NameServerForm


class NameServerDeleteView(generic.ObjectDeleteView):
    queryset = NameServer.objects.all()


class NameServerBulkImportView(generic.BulkImportView):
    queryset = NameServer.objects.all()
    model_form = NameServerCSVForm
    table = NameServerTable


class NameServerBulkDeleteView(generic.BulkDeleteView):
    queryset = NameServer.objects.all()
    table = NameServerTable


#
# Record
#


class RecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=False)
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    table = RecordTable
    template_name = "netbox_dns/record_list.html"


class ManagedRecordListView(generic.ObjectListView):
    queryset = Record.objects.filter(managed=True)
    filterset = RecordFilter
    filterset_form = RecordFilterForm
    table = ManagedRecordTable
    template_name = "netbox_dns/managed_record_list.html"


class RecordView(generic.ObjectView):
    """Display Zone details"""

    queryset = Record.objects.all()


class RecordEditView(generic.ObjectEditView):
    """View for editing a Record instance."""

    queryset = Record.objects.filter(managed=False)
    model_form = RecordForm


class RecordDeleteView(generic.ObjectDeleteView):
    queryset = Record.objects.filter(managed=False)


class RecordBulkImportView(generic.BulkImportView):
    queryset = Record.objects.filter(managed=False)
    model_form = RecordCSVForm
    table = RecordTable


class RecordBulkEditView(generic.BulkEditView):
    queryset = Record.objects.filter(managed=False)
    filterset = RecordFilter
    table = RecordTable
    form = RecordBulkEditForm


class RecordBulkDeleteView(generic.BulkDeleteView):
    queryset = Record.objects.filter(managed=False)
    table = RecordTable
