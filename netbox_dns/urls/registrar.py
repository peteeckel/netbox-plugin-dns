from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import Registrar
from netbox_dns.views import (
    RegistrarListView,
    RegistrarView,
    RegistrarDeleteView,
    RegistrarEditView,
    RegistrarBulkImportView,
    RegistrarBulkEditView,
    RegistrarBulkDeleteView,
    RegistrarZoneListView,
)

registrar_urlpatterns = [
    path("registrars/", RegistrarListView.as_view(), name="registrar_list"),
    path("registrars/add/", RegistrarEditView.as_view(), name="registrar_add"),
    path(
        "registrars/import/",
        RegistrarBulkImportView.as_view(),
        name="registrar_import",
    ),
    path(
        "registrars/edit/",
        RegistrarBulkEditView.as_view(),
        name="registrar_bulk_edit",
    ),
    path(
        "registrars/delete/",
        RegistrarBulkDeleteView.as_view(),
        name="registrar_bulk_delete",
    ),
    path("registrars/<int:pk>/", RegistrarView.as_view(), name="registrar"),
    path(
        "registrars/<int:pk>/edit/",
        RegistrarEditView.as_view(),
        name="registrar_edit",
    ),
    path(
        "registrars/<int:pk>/delete/",
        RegistrarDeleteView.as_view(),
        name="registrar_delete",
    ),
    path(
        "registrars/<int:pk>/zones/",
        RegistrarZoneListView.as_view(),
        name="registrar_zones",
    ),
    path(
        "registrars/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="registrar_journal",
        kwargs={"model": Registrar},
    ),
    path(
        "registrars/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="registrar_changelog",
        kwargs={"model": Registrar},
    ),
]
