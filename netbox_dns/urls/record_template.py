from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import RecordTemplate
from netbox_dns.views import (
    RecordTemplateListView,
    RecordTemplateView,
    RecordTemplateEditView,
    RecordTemplateDeleteView,
    RecordTemplateBulkImportView,
    RecordTemplateBulkEditView,
    RecordTemplateBulkDeleteView,
)

recordtemplate_urlpatterns = [
    path(
        "recordtemplates/", RecordTemplateListView.as_view(), name="recordtemplate_list"
    ),
    path(
        "recordtemplates/add/",
        RecordTemplateEditView.as_view(),
        name="recordtemplate_add",
    ),
    path(
        "recordtemplates/import/",
        RecordTemplateBulkImportView.as_view(),
        name="recordtemplate_import",
    ),
    path(
        "recordtemplates/edit/",
        RecordTemplateBulkEditView.as_view(),
        name="recordtemplate_bulk_edit",
    ),
    path(
        "recordtemplates/delete/",
        RecordTemplateBulkDeleteView.as_view(),
        name="recordtemplate_bulk_delete",
    ),
    path(
        "recordtemplates/<int:pk>/", RecordTemplateView.as_view(), name="recordtemplate"
    ),
    path(
        "recordtemplates/<int:pk>/edit/",
        RecordTemplateEditView.as_view(),
        name="recordtemplate_edit",
    ),
    path(
        "recordtemplates/<int:pk>/delete/",
        RecordTemplateDeleteView.as_view(),
        name="recordtemplate_delete",
    ),
    path(
        "recordtemplates/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="recordtemplate_journal",
        kwargs={"model": RecordTemplate},
    ),
    path(
        "recordtemplates/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="recordtemplate_changelog",
        kwargs={"model": RecordTemplate},
    ),
]
