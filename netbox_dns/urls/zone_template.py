from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import ZoneTemplate
from netbox_dns.views import (
    ZoneTemplateListView,
    ZoneTemplateView,
    ZoneTemplateDeleteView,
    ZoneTemplateEditView,
    ZoneTemplateBulkImportView,
    ZoneTemplateBulkEditView,
    ZoneTemplateBulkDeleteView,
)

zonetemplate_urlpatterns = [
    path("zonetemplates/", ZoneTemplateListView.as_view(), name="zonetemplate_list"),
    path("zonetemplates/add/", ZoneTemplateEditView.as_view(), name="zonetemplate_add"),
    path(
        "zonetemplates/import/",
        ZoneTemplateBulkImportView.as_view(),
        name="zonetemplate_import",
    ),
    path(
        "zonetemplates/edit/",
        ZoneTemplateBulkEditView.as_view(),
        name="zonetemplate_bulk_edit",
    ),
    path(
        "zonetemplates/delete/",
        ZoneTemplateBulkDeleteView.as_view(),
        name="zonetemplate_bulk_delete",
    ),
    path("zonetemplates/<int:pk>/", ZoneTemplateView.as_view(), name="zonetemplate"),
    path(
        "zonetemplates/<int:pk>/delete/",
        ZoneTemplateDeleteView.as_view(),
        name="zonetemplate_delete",
    ),
    path(
        "zonetemplates/<int:pk>/edit/",
        ZoneTemplateEditView.as_view(),
        name="zonetemplate_edit",
    ),
    path(
        "zonetemplates/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="zonetemplate_journal",
        kwargs={"model": ZoneTemplate},
    ),
    path(
        "zonetemplates/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="zonetemplate_changelog",
        kwargs={"model": ZoneTemplate},
    ),
]
