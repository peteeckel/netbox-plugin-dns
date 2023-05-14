from netbox.api.routers import NetBoxRouter

from netbox_dns.api.views import (
    NetBoxDNSRootView,
    ViewViewSet,
    ZoneViewSet,
    NameServerViewSet,
    RecordViewSet,
)

router = NetBoxRouter()
router.APIRootView = NetBoxDNSRootView

router.register("views", ViewViewSet)
router.register("zones", ZoneViewSet)
router.register("nameservers", NameServerViewSet)
router.register("records", RecordViewSet)

urlpatterns = router.urls
