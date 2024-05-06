from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from netbox_dns.models import Contact
from netbox_dns.views import (
    ContactListView,
    ContactView,
    ContactDeleteView,
    ContactEditView,
    ContactBulkImportView,
    ContactBulkEditView,
    ContactBulkDeleteView,
    ContactZoneListView,
)

contact_urlpatterns = [
    path("contacts/", ContactListView.as_view(), name="contact_list"),
    path("contacts/add/", ContactEditView.as_view(), name="contact_add"),
    path("contacts/import/", ContactBulkImportView.as_view(), name="contact_import"),
    path("contacts/edit/", ContactBulkEditView.as_view(), name="contact_bulk_edit"),
    path(
        "contacts/delete/",
        ContactBulkDeleteView.as_view(),
        name="contact_bulk_delete",
    ),
    path("contacts/<int:pk>/", ContactView.as_view(), name="contact"),
    path("contacts/<int:pk>/edit/", ContactEditView.as_view(), name="contact_edit"),
    path(
        "contacts/<int:pk>/delete/",
        ContactDeleteView.as_view(),
        name="contact_delete",
    ),
    path(
        "contacts/<int:pk>/zones/",
        ContactZoneListView.as_view(),
        name="contact_zones",
    ),
    path(
        "contacts/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="contact_journal",
        kwargs={"model": Contact},
    ),
    path(
        "contacts/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contact_changelog",
        kwargs={"model": Contact},
    ),
]
