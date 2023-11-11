from extras.plugins import PluginMenuButton, PluginMenuItem
from extras.plugins import PluginMenu
from utilities.choices import ButtonColorChoices

view_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:view_list",
    link_text="Views",
    permissions=["netbox_dns.view_view"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:view_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_view"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:view_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_view"],
        ),
    ),
)

zone_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:zone_list",
    link_text="Zones",
    permissions=["netbox_dns.view_zone"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:zone_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_zone"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:zone_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_zone"],
        ),
    ),
)

nameserver_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:nameserver_list",
    link_text="Nameservers",
    permissions=["netbox_dns.view_nameserver"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:nameserver_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_nameserver"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:nameserver_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_nameserver"],
        ),
    ),
)

record_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:record_list",
    link_text="Records",
    permissions=["netbox_dns.view_record"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:record_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_record"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:record_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_record"],
        ),
    ),
)

managed_record_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:managed_record_list",
    link_text="Managed Records",
    permissions=["netbox_dns.view_record"],
)

registrar_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:registrar_list",
    link_text="Registrars",
    permissions=["netbox_dns.view_registrar"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:registrar_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_registrar"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:registrar_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_registrar"],
        ),
    ),
)

contact_menu_item = PluginMenuItem(
    link="plugins:netbox_dns:contact_list",
    link_text="Contacts",
    permissions=["netbox_dns.view_contact"],
    buttons=(
        PluginMenuButton(
            "plugins:netbox_dns:contact_add",
            "Add",
            "mdi mdi-plus-thick",
            ButtonColorChoices.GREEN,
            permissions=["netbox_dns.add_contact"],
        ),
        PluginMenuButton(
            "plugins:netbox_dns:contact_import",
            "Import",
            "mdi mdi-upload",
            ButtonColorChoices.CYAN,
            permissions=["netbox_dns.add_contact"],
        ),
    ),
)

menu = PluginMenu(
    label="NetBox DNS",
    groups=(
        (
            "DNS Configuration",
            (
                view_menu_item,
                zone_menu_item,
                nameserver_menu_item,
                record_menu_item,
                managed_record_menu_item,
            ),
        ),
        (
            "Domain Registration",
            (
                registrar_menu_item,
                contact_menu_item,
            ),
        ),
    ),
    icon_class="mdi mdi-dns",
)
