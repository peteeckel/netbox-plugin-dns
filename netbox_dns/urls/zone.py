from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import Zone
from netbox_dns.views import (
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
    ZoneChildZoneListView,
)

zone_urlpatterns = [
    path("zones/", ZoneListView.as_view(), name="zone_list"),
    path("zones/add/", ZoneEditView.as_view(), name="zone_add"),
    path("zones/import/", ZoneBulkImportView.as_view(), name="zone_import"),
    path("zones/edit/", ZoneBulkEditView.as_view(), name="zone_bulk_edit"),
    path("zones/delete/", ZoneBulkDeleteView.as_view(), name="zone_bulk_delete"),
    path("zones/<int:pk>/", ZoneView.as_view(), name="zone"),
    path("zones/<int:pk>/delete/", ZoneDeleteView.as_view(), name="zone_delete"),
    path("zones/<int:pk>/edit/", ZoneEditView.as_view(), name="zone_edit"),
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
        "zones/<int:pk>/childzones/",
        ZoneChildZoneListView.as_view(),
        name="zone_child_zones",
    ),
    path(
        "zones/<int:pk>/registration/",
        ZoneRegistrationView.as_view(),
        name="zone_registration",
    ),
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
]
