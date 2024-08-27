from .registration_contact import registrationcontact_urlpatterns
from .nameserver import nameserver_urlpatterns
from .record import record_urlpatterns
from .record_template import recordtemplate_urlpatterns
from .registrar import registrar_urlpatterns
from .view import view_urlpatterns
from .zone import zone_urlpatterns
from .zone_template import zonetemplate_urlpatterns

app_name = "netbox_dns"

urlpatterns = (
    registrationcontact_urlpatterns
    + nameserver_urlpatterns
    + record_urlpatterns
    + recordtemplate_urlpatterns
    + registrar_urlpatterns
    + view_urlpatterns
    + zone_urlpatterns
    + zonetemplate_urlpatterns
)
