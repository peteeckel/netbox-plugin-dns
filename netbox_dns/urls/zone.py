from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    ZoneView,
    ZoneListView,
    ZoneEditView,
    ZoneDeleteView,
    ZoneBulkImportView,
    ZoneBulkEditView,
    ZoneBulkDeleteView,
)

zone_urlpatterns = [
    path("zones/<int:pk>/", ZoneView.as_view(), name="zone"),
    path("zones/", ZoneListView.as_view(), name="zone_list"),
    path("zones/add/", ZoneEditView.as_view(), name="zone_add"),
    path("zones/<int:pk>/edit/", ZoneEditView.as_view(), name="zone_edit"),
    path("zones/<int:pk>/delete/", ZoneDeleteView.as_view(), name="zone_delete"),
    path("zones/import/", ZoneBulkImportView.as_view(), name="zone_import"),
    path("zones/edit/", ZoneBulkEditView.as_view(), name="zone_bulk_edit"),
    path("zones/delete/", ZoneBulkDeleteView.as_view(), name="zone_bulk_delete"),
    path("zones/<int:pk>/", include(get_model_urls("netbox_dns", "zone"))),
]
