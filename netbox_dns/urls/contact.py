from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    ContactView,
    ContactListView,
    ContactEditView,
    ContactDeleteView,
    ContactBulkImportView,
    ContactBulkEditView,
    ContactBulkDeleteView,
)

contact_urlpatterns = [
    path("contacts/<int:pk>/", ContactView.as_view(), name="contact"),
    path("contacts/", ContactListView.as_view(), name="contact_list"),
    path("contacts/add/", ContactEditView.as_view(), name="contact_add"),
    path("contacts/<int:pk>/edit/", ContactEditView.as_view(), name="contact_edit"),
    path(
        "contacts/<int:pk>/delete/", ContactDeleteView.as_view(), name="contact_delete"
    ),
    path("contacts/import/", ContactBulkImportView.as_view(), name="contact_import"),
    path("contacts/edit/", ContactBulkEditView.as_view(), name="contact_bulk_edit"),
    path(
        "contacts/delete/", ContactBulkDeleteView.as_view(), name="contact_bulk_delete"
    ),
    path("contacts/<int:pk>/", include(get_model_urls("netbox_dns", "contact"))),
]
