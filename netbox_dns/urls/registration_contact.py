from django.urls import include, path

from utilities.urls import get_model_urls

from netbox_dns.views import (
    RegistrationContactView,
    RegistrationContactListView,
    RegistrationContactEditView,
    RegistrationContactDeleteView,
    RegistrationContactBulkImportView,
    RegistrationContactBulkEditView,
    RegistrationContactBulkDeleteView,
)

registrationcontact_urlpatterns = [
    path(
        "registrationcontacts/<int:pk>/",
        RegistrationContactView.as_view(),
        name="registrationcontact",
    ),
    path(
        "registrationcontacts/",
        RegistrationContactListView.as_view(),
        name="registrationcontact_list",
    ),
    path(
        "registrationcontacts/add/",
        RegistrationContactEditView.as_view(),
        name="registrationcontact_add",
    ),
    path(
        "registrationcontacts/<int:pk>/edit/",
        RegistrationContactEditView.as_view(),
        name="registrationcontact_edit",
    ),
    path(
        "registrationcontacts/<int:pk>/delete/",
        RegistrationContactDeleteView.as_view(),
        name="registrationcontact_delete",
    ),
    path(
        "registrationcontacts/import/",
        RegistrationContactBulkImportView.as_view(),
        name="registrationcontact_import",
    ),
    path(
        "registrationcontacts/edit/",
        RegistrationContactBulkEditView.as_view(),
        name="registrationcontact_bulk_edit",
    ),
    path(
        "registrationcontacts/delete/",
        RegistrationContactBulkDeleteView.as_view(),
        name="registrationcontact_bulk_delete",
    ),
    path(
        "registrationcontacts/<int:pk>/",
        include(get_model_urls("netbox_dns", "registrationcontact")),
    ),
]
