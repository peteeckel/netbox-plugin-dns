from .contact import contact_urlpatterns
from .nameserver import nameserver_urlpatterns
from .record import record_urlpatterns
from .registrar import registrar_urlpatterns
from .view import view_urlpatterns
from .zone import zone_urlpatterns

app_name = "netbox_dns"

urlpatterns = (
    contact_urlpatterns
    + nameserver_urlpatterns
    + record_urlpatterns
    + registrar_urlpatterns
    + view_urlpatterns
    + zone_urlpatterns
)
