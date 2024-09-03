from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    ViewView,
    ViewListView,
    ViewEditView,
    ViewDeleteView,
    ViewBulkImportView,
    ViewBulkEditView,
    ViewBulkDeleteView,
    ViewPrefixEditView,
)

view_urlpatterns = [
    path("views/<int:pk>/", ViewView.as_view(), name="view"),
    path("views/", ViewListView.as_view(), name="view_list"),
    path("views/add/", ViewEditView.as_view(), name="view_add"),
    path("views/<int:pk>/edit/", ViewEditView.as_view(), name="view_edit"),
    path("views/<int:pk>/delete/", ViewDeleteView.as_view(), name="view_delete"),
    path("views/import/", ViewBulkImportView.as_view(), name="view_import"),
    path("views/edit/", ViewBulkEditView.as_view(), name="view_bulk_edit"),
    path("views/delete/", ViewBulkDeleteView.as_view(), name="view_bulk_delete"),
    path("views/<int:pk>/", include(get_model_urls("netbox_dns", "view"))),
    path(
        "prefixes/<int:pk>/assign-views/",
        ViewPrefixEditView.as_view(),
        name="prefix_views",
    ),
]
