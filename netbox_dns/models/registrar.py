from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search


__all__ = (
    "Registrar",
    "RegistrarIndex",
)


class Registrar(NetBoxModel):
    class Meta:
        verbose_name = _("Registrar")
        verbose_name_plural = _("Registrars")

        ordering = (
            "name",
            "iana_id",
        )

    def __str__(self):
        return str(self.name)

    # +
    # Data fields according to https://www.icann.org/resources/pages/rdds-labeling-policy-2017-02-01-en
    # -
    name = models.CharField(
        verbose_name=_("Name"),
        unique=True,
        max_length=255,
        db_collation="natural_sort",
    )
    description = models.CharField(
        verbose_name=_("Description"),
        blank=True,
        max_length=200,
    )
    iana_id = models.IntegerField(
        verbose_name=_("IANA ID"),
        null=True,
        blank=True,
    )
    referral_url = models.URLField(
        verbose_name=_("Referral URL"),
        max_length=255,
        blank=True,
    )
    whois_server = models.CharField(
        verbose_name=_("WHOIS Server"),
        max_length=255,
        blank=True,
    )
    address = models.CharField(
        verbose_name=_("Address"),
        max_length=200,
        blank=True,
    )
    abuse_email = models.EmailField(
        verbose_name=_("Abuse Email"),
        blank=True,
    )
    abuse_phone = models.CharField(
        verbose_name=_("Abuse Phone"),
        max_length=50,
        blank=True,
    )


@register_search
class RegistrarIndex(SearchIndex):
    model = Registrar

    fields = (
        ("name", 100),
        ("iana_id", 100),
    )
