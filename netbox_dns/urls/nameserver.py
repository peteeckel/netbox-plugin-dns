from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import NameServer
from netbox_dns.views import (
    NameServerListView,
    NameServerView,
    NameServerEditView,
    NameServerDeleteView,
    NameServerBulkImportView,
    NameServerBulkEditView,
    NameServerBulkDeleteView,
    NameServerZoneListView,
    NameServerSOAZoneListView,
)

nameserver_urlpatterns = [
    path("nameservers/", NameServerListView.as_view(), name="nameserver_list"),
    path("nameservers/add/", NameServerEditView.as_view(), name="nameserver_add"),
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
    path("nameservers/<int:pk>/", NameServerView.as_view(), name="nameserver"),
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
        "nameservers/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="nameserver_journal",
        kwargs={"model": NameServer},
    ),
    path(
        "nameservers/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="nameserver_changelog",
        kwargs={"model": NameServer},
    ),
    path(
        "nameservers/<int:pk>/zones/",
        NameServerZoneListView.as_view(),
        name="nameserver_zones",
    ),
    path(
        "nameservers/<int:pk>/soazones/",
        NameServerSOAZoneListView.as_view(),
        name="nameserver_soa_zones",
    ),
]
