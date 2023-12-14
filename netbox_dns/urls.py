from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import View, Zone, Record, NameServer, Contact, Registrar
from netbox_dns.views import (
    # zone
    ZoneListView,
    ZoneView,
    ZoneDeleteView,
    ZoneEditView,
    ZoneBulkImportView,
    ZoneBulkEditView,
    ZoneBulkDeleteView,
    ZoneRecordListView,
    ZoneManagedRecordListView,
    ZoneRegistrationView,
    ZoneRFC2317ChildZoneListView,
    # nameserver
    NameServerListView,
    NameServerView,
    NameServerEditView,
    NameServerDeleteView,
    NameServerBulkImportView,
    NameServerBulkEditView,
    NameServerBulkDeleteView,
    NameServerZoneListView,
    NameServerSOAZoneListView,
    # record
    RecordListView,
    RecordView,
    RecordEditView,
    RecordDeleteView,
    RecordBulkImportView,
    RecordBulkEditView,
    RecordBulkDeleteView,
    # managed record
    ManagedRecordListView,
    # view
    ViewListView,
    ViewView,
    ViewDeleteView,
    ViewEditView,
    ViewBulkImportView,
    ViewBulkEditView,
    ViewBulkDeleteView,
    ViewZoneListView,
    # contact
    ContactListView,
    ContactView,
    ContactDeleteView,
    ContactEditView,
    ContactBulkImportView,
    ContactBulkEditView,
    ContactBulkDeleteView,
    ContactZoneListView,
    # registrar
    RegistrarListView,
    RegistrarView,
    RegistrarDeleteView,
    RegistrarEditView,
    RegistrarBulkImportView,
    RegistrarBulkEditView,
    RegistrarBulkDeleteView,
    RegistrarZoneListView,
)

app_name = "netbox_dns"

urlpatterns = [
    #
    # Zone urls
    #
    path("zones/", ZoneListView.as_view(), name="zone_list"),
    path("zones/add/", ZoneEditView.as_view(), name="zone_add"),
    path("zones/import/", ZoneBulkImportView.as_view(), name="zone_import"),
    path("zones/edit/", ZoneBulkEditView.as_view(), name="zone_bulk_edit"),
    path("zones/delete/", ZoneBulkDeleteView.as_view(), name="zone_bulk_delete"),
    path("zones/<int:pk>/", ZoneView.as_view(), name="zone"),
    path("zones/<int:pk>/delete/", ZoneDeleteView.as_view(), name="zone_delete"),
    path("zones/<int:pk>/edit/", ZoneEditView.as_view(), name="zone_edit"),
    path(
        "zones/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="zone_journal",
        kwargs={"model": Zone},
    ),
    path(
        "zones/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="zone_changelog",
        kwargs={"model": Zone},
    ),
    path("zones/<int:pk>/records/", ZoneRecordListView.as_view(), name="zone_records"),
    path(
        "zones/<int:pk>/managedrecords/",
        ZoneManagedRecordListView.as_view(),
        name="zone_managed_records",
    ),
    path(
        "zones/<int:pk>/rfc2317childzones/",
        ZoneRFC2317ChildZoneListView.as_view(),
        name="zone_rfc2317_child_zones",
    ),
    path(
        "zones/<int:pk>/registration/",
        ZoneRegistrationView.as_view(),
        name="zone_registration",
    ),
    #
    # NameServer urls
    #
    path("nameservers/", NameServerListView.as_view(), name="nameserver_list"),
    path("nameservers/add/", NameServerEditView.as_view(), name="nameserver_add"),
    path(
        "nameservers/import/",
        NameServerBulkImportView.as_view(),
        name="nameserver_import",
    ),
    path(
        "nameservers/edit/",
        NameServerBulkEditView.as_view(),
        name="nameserver_bulk_edit",
    ),
    path(
        "nameservers/delete/",
        NameServerBulkDeleteView.as_view(),
        name="nameserver_bulk_delete",
    ),
    path("nameservers/<int:pk>/", NameServerView.as_view(), name="nameserver"),
    path(
        "nameservers/<int:pk>/edit",
        NameServerEditView.as_view(),
        name="nameserver_edit",
    ),
    path(
        "nameservers/<int:pk>/delete",
        NameServerDeleteView.as_view(),
        name="nameserver_delete",
    ),
    path(
        "nameservers/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="nameserver_journal",
        kwargs={"model": NameServer},
    ),
    path(
        "nameservers/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="nameserver_changelog",
        kwargs={"model": NameServer},
    ),
    path(
        "nameservers/<int:pk>/zones/",
        NameServerZoneListView.as_view(),
        name="nameserver_zones",
    ),
    path(
        "nameservers/<int:pk>/soazones/",
        NameServerSOAZoneListView.as_view(),
        name="nameserver_soa_zones",
    ),
    #
    # Record urls
    #
    path("records/", RecordListView.as_view(), name="record_list"),
    path("records/add/", RecordEditView.as_view(), name="record_add"),
    path("records/import/", RecordBulkImportView.as_view(), name="record_import"),
    path("records/edit/", RecordBulkEditView.as_view(), name="record_bulk_edit"),
    path("records/delete/", RecordBulkDeleteView.as_view(), name="record_bulk_delete"),
    path("records/<int:pk>/", RecordView.as_view(), name="record"),
    path("records/<int:pk>/edit/", RecordEditView.as_view(), name="record_edit"),
    path("records/<int:pk>/delete/", RecordDeleteView.as_view(), name="record_delete"),
    path(
        "records/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="record_journal",
        kwargs={"model": Record},
    ),
    path(
        "records/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="record_changelog",
        kwargs={"model": Record},
    ),
    path(
        "managedrecords/", ManagedRecordListView.as_view(), name="managed_record_list"
    ),
    #
    # View urls
    #
    path("views/", ViewListView.as_view(), name="view_list"),
    path("views/add/", ViewEditView.as_view(), name="view_add"),
    path("views/import/", ViewBulkImportView.as_view(), name="view_import"),
    path("views/edit/", ViewBulkEditView.as_view(), name="view_bulk_edit"),
    path("views/delete/", ViewBulkDeleteView.as_view(), name="view_bulk_delete"),
    path("views/<int:pk>/", ViewView.as_view(), name="view"),
    path("views/<int:pk>/edit/", ViewEditView.as_view(), name="view_edit"),
    path("views/<int:pk>/delete/", ViewDeleteView.as_view(), name="view_delete"),
    path("views/<int:pk>/zones/", ViewZoneListView.as_view(), name="view_zones"),
    path(
        "views/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="view_journal",
        kwargs={"model": View},
    ),
    path(
        "views/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="view_changelog",
        kwargs={"model": View},
    ),
    #
    # Contact urls
    #
    path("contacts/", ContactListView.as_view(), name="contact_list"),
    path("contacts/add/", ContactEditView.as_view(), name="contact_add"),
    path("contacts/import/", ContactBulkImportView.as_view(), name="contact_import"),
    path("contacts/edit/", ContactBulkEditView.as_view(), name="contact_bulk_edit"),
    path(
        "contacts/delete/",
        ContactBulkDeleteView.as_view(),
        name="contact_bulk_delete",
    ),
    path("contacts/<int:pk>/", ContactView.as_view(), name="contact"),
    path("contacts/<int:pk>/edit/", ContactEditView.as_view(), name="contact_edit"),
    path(
        "contacts/<int:pk>/delete/",
        ContactDeleteView.as_view(),
        name="contact_delete",
    ),
    path(
        "contacts/<int:pk>/zones/",
        ContactZoneListView.as_view(),
        name="contact_zones",
    ),
    path(
        "contacts/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="contact_journal",
        kwargs={"model": Contact},
    ),
    path(
        "contacts/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contact_changelog",
        kwargs={"model": Contact},
    ),
    #
    # Registrar urls
    #
    path("registrars/", RegistrarListView.as_view(), name="registrar_list"),
    path("registrars/add/", RegistrarEditView.as_view(), name="registrar_add"),
    path(
        "registrars/import/",
        RegistrarBulkImportView.as_view(),
        name="registrar_import",
    ),
    path(
        "registrars/edit/",
        RegistrarBulkEditView.as_view(),
        name="registrar_bulk_edit",
    ),
    path(
        "registrars/delete/",
        RegistrarBulkDeleteView.as_view(),
        name="registrar_bulk_delete",
    ),
    path("registrars/<int:pk>/", RegistrarView.as_view(), name="registrar"),
    path(
        "registrars/<int:pk>/edit/",
        RegistrarEditView.as_view(),
        name="registrar_edit",
    ),
    path(
        "registrars/<int:pk>/delete/",
        RegistrarDeleteView.as_view(),
        name="registrar_delete",
    ),
    path(
        "registrars/<int:pk>/zones/",
        RegistrarZoneListView.as_view(),
        name="registrar_zones",
    ),
    path(
        "registrars/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="registrar_journal",
        kwargs={"model": Registrar},
    ),
    path(
        "registrars/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="registrar_changelog",
        kwargs={"model": Registrar},
    ),
]
