from netbox.api.routers import NetBoxRouter

from netbox_dns.api.views import (
    NetBoxDNSRootView,
    ViewViewSet,
    ZoneViewSet,
    NameServerViewSet,
    RecordViewSet,
    RegistrarViewSet,
    RegistrationContactViewSet,
    ZoneTemplateViewSet,
    RecordTemplateViewSet,
    PrefixViewSet,
)

router = NetBoxRouter()
router.APIRootView = NetBoxDNSRootView

router.register("views", ViewViewSet)
router.register("zones", ZoneViewSet)
router.register("nameservers", NameServerViewSet)
router.register("records", RecordViewSet)
router.register("registrars", RegistrarViewSet)
router.register("contacts", RegistrationContactViewSet)
router.register("zonetemplates", ZoneTemplateViewSet)
router.register("recordtemplates", RecordTemplateViewSet)

router.register("prefixes", PrefixViewSet)

urlpatterns = router.urls
