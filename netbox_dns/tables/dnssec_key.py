import django_tables2 as tables
from django.utils.translation import gettext_lazy as _


from netbox.tables import (
    NetBoxTable,
    ChoiceFieldColumn,
    TagColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import DNSSECKey


__all__ = ("DNSSECKeyTable",)


class DNSSECKeyTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    type = ChoiceFieldColumn(
        verbose_name=_("Key Type"),
    )
    lifetime = tables.Column(
        verbose_name=_("Lifetime"),
    )
    algorithm = ChoiceFieldColumn(
        verbose_name=_("Algorithm"),
    )
    key_size = tables.Column(
        verbose_name=_("Key Size"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:dnsseckey_list",
    )

    class Meta(NetBoxTable.Meta):
        model = DNSSECKey
        fields = ("description",)
        default_columns = (
            "name",
            "type",
            "algorithm",
            "key_size",
            "tags",
        )
