from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    NameServerView,
    NameServerListView,
    NameServerEditView,
    NameServerDeleteView,
    NameServerBulkImportView,
    NameServerBulkEditView,
    NameServerBulkDeleteView,
)

nameserver_urlpatterns = [
    path("nameservers/<int:pk>/", NameServerView.as_view(), name="nameserver"),
    path("nameservers/", NameServerListView.as_view(), name="nameserver_list"),
    path("nameservers/add/", NameServerEditView.as_view(), name="nameserver_add"),
    path(
        "nameservers/<int:pk>/edit",
        NameServerEditView.as_view(),
        name="nameserver_edit",
    ),
    path(
        "nameservers/<int:pk>/delete",
        NameServerDeleteView.as_view(),
        name="nameserver_delete",
    ),
    path(
        "nameservers/import/",
        NameServerBulkImportView.as_view(),
        name="nameserver_import",
    ),
    path(
        "nameservers/edit/",
        NameServerBulkEditView.as_view(),
        name="nameserver_bulk_edit",
    ),
    path(
        "nameservers/delete/",
        NameServerBulkDeleteView.as_view(),
        name="nameserver_bulk_delete",
    ),
    path("nameservers/<int:pk>/", include(get_model_urls("netbox_dns", "nameserver"))),
]
