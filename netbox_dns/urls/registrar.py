from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    RegistrarView,
    RegistrarListView,
    RegistrarEditView,
    RegistrarDeleteView,
    RegistrarBulkImportView,
    RegistrarBulkEditView,
    RegistrarBulkDeleteView,
)

registrar_urlpatterns = [
    path("registrars/<int:pk>/", RegistrarView.as_view(), name="registrar"),
    path("registrars/", RegistrarListView.as_view(), name="registrar_list"),
    path("registrars/add/", RegistrarEditView.as_view(), name="registrar_add"),
    path(
        "registrars/<int:pk>/edit/", RegistrarEditView.as_view(), name="registrar_edit"
    ),
    path(
        "registrars/delete/",
        RegistrarBulkDeleteView.as_view(),
        name="registrar_bulk_delete",
    ),
    path(
        "registrars/import/", RegistrarBulkImportView.as_view(), name="registrar_import"
    ),
    path(
        "registrars/edit/", RegistrarBulkEditView.as_view(), name="registrar_bulk_edit"
    ),
    path(
        "registrars/<int:pk>/delete/",
        RegistrarDeleteView.as_view(),
        name="registrar_delete",
    ),
    path("registrars/<int:pk>/", include(get_model_urls("netbox_dns", "registrar"))),
]
