from django.urls import include, path

from utilities.urls import get_model_urls

# +
# Import views so the register_model_view is run. This is required for the
# URLs to be set up properly with get_model_urls().
# -
from .views import *  # noqa: F401


app_name = "netbox_dns"

urlpatterns = (
    path(
        "nameservers/",
        include(get_model_urls("netbox_dns", "nameserver", detail=False)),
    ),
    path(
        "nameservers/<int:pk>/",
        include(get_model_urls("netbox_dns", "nameserver")),
    ),
    path(
        "recordtemplates/",
        include(get_model_urls("netbox_dns", "recordtemplate", detail=False)),
    ),
    path(
        "recordtemplates/<int:pk>/",
        include(get_model_urls("netbox_dns", "recordtemplate")),
    ),
    path(
        "records/",
        include(get_model_urls("netbox_dns", "record", detail=False)),
    ),
    path(
        "records/<int:pk>/",
        include(get_model_urls("netbox_dns", "record")),
    ),
    path(
        "registrars",
        include(get_model_urls("netbox_dns", "registrar", detail=False)),
    ),
    path(
        "registrars/<int:pk>/",
        include(get_model_urls("netbox_dns", "registrar")),
    ),
    path(
        "registrationcontacts/",
        include(get_model_urls("netbox_dns", "registrationcontact", detail=False)),
    ),
    path(
        "registrationcontacts/<int:pk>/",
        include(get_model_urls("netbox_dns", "registrationcontact")),
    ),
    path(
        "views/",
        include(get_model_urls("netbox_dns", "view", detail=False)),
    ),
    path(
        "views/<int:pk>/",
        include(get_model_urls("netbox_dns", "view")),
    ),
    path(
        "zonetemplates/",
        include(get_model_urls("netbox_dns", "zonetemplate", detail=False)),
    ),
    path(
        "zonetemplates/<int:pk>/",
        include(get_model_urls("netbox_dns", "zonetemplate")),
    ),
    path(
        "zones/",
        include(get_model_urls("netbox_dns", "zone", detail=False)),
    ),
    path(
        "zones/<int:pk>/",
        include(get_model_urls("netbox_dns", "zone")),
    ),
    path(
        "dnsseckeytemplates/",
        include(get_model_urls("netbox_dns", "dnsseckeytemplate", detail=False)),
    ),
    path(
        "dnsseckeytemplates/<int:pk>/",
        include(get_model_urls("netbox_dns", "dnsseckeytemplate")),
    ),
    path(
        "dnssecpolicies/",
        include(get_model_urls("netbox_dns", "dnssecpolicy", detail=False)),
    ),
    path(
        "dnssecpolicies/<int:pk>/",
        include(get_model_urls("netbox_dns", "dnssecpolicy")),
    ),
)
