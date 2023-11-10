from netbox.api.routers import NetBoxRouter

from netbox_dns.api.views import (
    NetBoxDNSRootView,
    ViewViewSet,
    ZoneViewSet,
    NameServerViewSet,
    RecordViewSet,
    RegistrarViewSet,
    ContactViewSet,
)

router = NetBoxRouter()
router.APIRootView = NetBoxDNSRootView

router.register("views", ViewViewSet)
router.register("zones", ZoneViewSet)
router.register("nameservers", NameServerViewSet)
router.register("records", RecordViewSet)
router.register("registrars", RegistrarViewSet)
router.register("contacts", ContactViewSet)

urlpatterns = router.urls
