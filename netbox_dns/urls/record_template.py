from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    RecordTemplateView,
    RecordTemplateListView,
    RecordTemplateEditView,
    RecordTemplateDeleteView,
    RecordTemplateBulkImportView,
    RecordTemplateBulkEditView,
    RecordTemplateBulkDeleteView,
)

recordtemplate_urlpatterns = [
    path(
        "recordtemplates/<int:pk>/", RecordTemplateView.as_view(), name="recordtemplate"
    ),
    path(
        "recordtemplates/", RecordTemplateListView.as_view(), name="recordtemplate_list"
    ),
    path(
        "recordtemplates/add/",
        RecordTemplateEditView.as_view(),
        name="recordtemplate_add",
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
        "recordtemplates/<int:pk>/",
        include(get_model_urls("netbox_dns", "recordtemplate")),
    ),
]
