from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    ZoneTemplateView,
    ZoneTemplateListView,
    ZoneTemplateEditView,
    ZoneTemplateDeleteView,
    ZoneTemplateBulkImportView,
    ZoneTemplateBulkEditView,
    ZoneTemplateBulkDeleteView,
)

zonetemplate_urlpatterns = [
    path("zonetemplates/<int:pk>/", ZoneTemplateView.as_view(), name="zonetemplate"),
    path("zonetemplates/", ZoneTemplateListView.as_view(), name="zonetemplate_list"),
    path("zonetemplates/add/", ZoneTemplateEditView.as_view(), name="zonetemplate_add"),
    path(
        "zonetemplates/<int:pk>/edit/",
        ZoneTemplateEditView.as_view(),
        name="zonetemplate_edit",
    ),
    path(
        "zonetemplates/<int:pk>/delete/",
        ZoneTemplateDeleteView.as_view(),
        name="zonetemplate_delete",
    ),
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
    path(
        "zonetemplates/<int:pk>/", include(get_model_urls("netbox_dns", "zonetemplate"))
    ),
]
