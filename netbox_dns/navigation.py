from django.utils.translation import gettext_lazy as _

from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu
from netbox.plugins.utils import get_plugin_config

menu_name = get_plugin_config("netbox_dns", "menu_name")
top_level_menu = get_plugin_config("netbox_dns", "top_level_menu")

view_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:view_list",
    link_text=_("Views"),
    permissions=["netbox_dns.view_view"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:view_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_view"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:view_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_view"],
        ),
    ),
)

nameserver_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:nameserver_list",
    link_text=_("Nameservers"),
    permissions=["netbox_dns.view_nameserver"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:nameserver_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_nameserver"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:nameserver_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_nameserver"],
        ),
    ),
)

zone_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:zone_list",
    link_text=_("Zones"),
    permissions=["netbox_dns.view_zone"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:zone_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_zone"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:zone_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_zone"],
        ),
    ),
)

record_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:record_list",
    link_text=_("Records"),
    permissions=["netbox_dns.view_record"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:record_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_record"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:record_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_record"],
        ),
    ),
)

managed_record_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:record_list_managed",
    link_text=_("Managed Records"),
    permissions=["netbox_dns.view_record"],
)

zonetemplate_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:zonetemplate_list",
    link_text=_("Zone Templates"),
    permissions=["netbox_dns.view_zonetemplate"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:zonetemplate_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_zonetemplate"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:zonetemplate_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_zonetemplate"],
        ),
    ),
)

recordtemplate_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:recordtemplate_list",
    link_text=_("Record Templates"),
    permissions=["netbox_dns.view_recordtemplate"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:recordtemplate_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_recordtemplate"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:recordtemplate_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_recordtemplate"],
        ),
    ),
)

dnsseckeytemplate_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:dnsseckeytemplate_list",
    link_text=_("DNSSEC Key Templates"),
    permissions=["netbox_dns.view_dnsseckeytemplate"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:dnsseckeytemplate_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_dnsseckeytemplate"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:dnsseckeytemplate_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_dnsseckeytemplate"],
        ),
    ),
)

dnssecpolicy_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:dnssecpolicy_list",
    link_text=_("DNSSEC Policies"),
    permissions=["netbox_dns.view_dnssecpolicy"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:dnssecpolicy_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_dnssecpolicy"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:dnssecpolicy_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_dnssecpolicy"],
        ),
    ),
)

registrar_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:registrar_list",
    link_text=_("Registrars"),
    permissions=["netbox_dns.view_registrar"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:registrar_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_registrar"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:registrar_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_registrar"],
        ),
    ),
)

contact_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:registrationcontact_list",
    link_text=_("Registration Contacts"),
    permissions=["netbox_dns.view_registrationcontact"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:registrationcontact_add",
            _("Add"),
            "mdi mdi-plus-thick",
            permissions=["netbox_dns.add_registrationcontact"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:registrationcontact_bulk_import",
            _("Import"),
            "mdi mdi-upload",
            permissions=["netbox_dns.add_registrationcontact"],
        ),
    ),
)


if top_level_menu:
    menu = PluginMenu(
        label=menu_name,
        groups=(
            (
                _("DNS Configuration"),
                (
                    view_menu_item,
                    nameserver_menu_item,
                    zone_menu_item,
                    record_menu_item,
                    managed_record_menu_item,
                ),
            ),
            (
                _("Templates"),
                (
                    zonetemplate_menu_item,
                    recordtemplate_menu_item,
                ),
            ),
            (
                _("DNSSEC"),
                (
                    dnsseckeytemplate_menu_item,
                    dnssecpolicy_menu_item,
                ),
            ),
            (
                _("Domain Registration"),
                (
                    registrar_menu_item,
                    contact_menu_item,
                ),
            ),
        ),
        icon_class="mdi mdi-dns",
    )
else:
    menu_items = (
        view_menu_item,
        zone_menu_item,
        nameserver_menu_item,
        record_menu_item,
        managed_record_menu_item,
        dnsseckeytemplate_menu_item,
        dnssecpolicy_menu_item,
        registrar_menu_item,
        contact_menu_item,
    )
