from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import View
from netbox_dns.views import (
    ViewListView,
    ViewView,
    ViewDeleteView,
    ViewEditView,
    ViewBulkImportView,
    ViewBulkEditView,
    ViewBulkDeleteView,
    ViewZoneListView,
    ViewPrefixEditView,
)

view_urlpatterns = [
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
    path(
        "prefixes/<int:pk>/assign-views/",
        ViewPrefixEditView.as_view(),
        name="prefix_views",
    ),
]
