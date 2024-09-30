import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, TagColumn, ActionsColumn
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import ZoneTemplate


__all__ = (
    "ZoneTemplateTable",
    "ZoneTemplateDisplayTable",
)


class ZoneTemplateTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:zonetemplate_list",
    )
    registrar = tables.Column(
        verbose_name=_("Registrar"),
        linkify=True,
    )
    registrant = tables.Column(
        verbose_name=_("Registrant"),
        linkify=True,
    )
    admin_c = tables.Column(
        verbose_name=_("Administrative Contact"),
        linkify=True,
    )
    tech_c = tables.Column(
        verbose_name=_("Technical Contact"),
        linkify=True,
    )
    billing_c = tables.Column(
        verbose_name=_("Billing Contact"),
        linkify=True,
    )

    class Meta(NetBoxTable.Meta):
        model = ZoneTemplate
        fields = ("description",)
        default_columns = (
            "name",
            "tags",
        )


class ZoneTemplateDisplayTable(ZoneTemplateTable):
    actions = ActionsColumn(actions="")

    class Meta(NetBoxTable.Meta):
        model = ZoneTemplate
        fields = ("description",)
        default_columns = (
            "name",
            "description",
        )
