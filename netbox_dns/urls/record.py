from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    RecordView,
    RecordListView,
    RecordEditView,
    RecordDeleteView,
    RecordBulkImportView,
    RecordBulkEditView,
    RecordBulkDeleteView,
    ManagedRecordListView,
)

record_urlpatterns = [
    path("records/<int:pk>/", RecordView.as_view(), name="record"),
    path("records/", RecordListView.as_view(), name="record_list"),
    path("records/add/", RecordEditView.as_view(), name="record_add"),
    path("records/<int:pk>/edit/", RecordEditView.as_view(), name="record_edit"),
    path("records/<int:pk>/delete/", RecordDeleteView.as_view(), name="record_delete"),
    path("records/import/", RecordBulkImportView.as_view(), name="record_import"),
    path("records/edit/", RecordBulkEditView.as_view(), name="record_bulk_edit"),
    path("records/delete/", RecordBulkDeleteView.as_view(), name="record_bulk_delete"),
    path("records/<int:pk>/", include(get_model_urls("netbox_dns", "record"))),
    path(
        "managedrecords/", ManagedRecordListView.as_view(), name="managed_record_list"
    ),
]
