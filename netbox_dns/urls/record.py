from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import Record
from netbox_dns.views import (
    RecordListView,
    RecordView,
    RecordEditView,
    RecordDeleteView,
    RecordBulkImportView,
    RecordBulkEditView,
    RecordBulkDeleteView,
    ManagedRecordListView,
)

record_urlpatterns = [
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
]
