from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search


class Registrar(NetBoxModel):
    # +
    # Data fields according to https://www.icann.org/resources/pages/rdds-labeling-policy-2017-02-01-en
    # -
    name = models.CharField(
        unique=True,
        max_length=255,
    )
    iana_id = models.IntegerField(
        verbose_name="IANA ID",
        null=True,
        blank=True,
    )
    referral_url = models.URLField(
        verbose_name="Referral URL",
        max_length=255,
        blank=True,
    )
    whois_server = models.CharField(
        verbose_name="WHOIS Server",
        max_length=255,
        blank=True,
    )
    address = models.CharField(
        max_length=200,
        blank=True,
    )
    abuse_email = models.EmailField(
        verbose_name="Abuse Email",
        blank=True,
    )
    abuse_phone = models.CharField(
        verbose_name="Abuse Phone",
        max_length=50,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:registrar", kwargs={"pk": self.id})

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ("name", "iana_id")


@register_search
class RegistrarIndex(SearchIndex):
    model = Registrar
    fields = (
        ("name", 100),
        ("iana_id", 100),
    )
