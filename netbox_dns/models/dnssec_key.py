from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.models.features import ContactsMixin

from netbox_dns.choices import DNSSECKeyTypeChoices, DNSSECKeyAlgorithmChoices


__all__ = (
    "DNSSECKey",
    "DNSSECKeyIndex",
)


class DNSSECKey(ContactsMixin, NetBoxModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=200,
        blank=True,
    )

    type = models.CharField(
        verbose_name=_("Type"),
        choices=DNSSECKeyTypeChoices,
        max_length=3,
        blank=False,
        null=False,
    )
    lifetime = models.PositiveIntegerField(
        verbose_name=_("Lifetime"),
        blank=True,
        null=True,
    )
    algorithm = models.CharField(
        verbose_name=_("Algorithm"),
        choices=DNSSECKeyAlgorithmChoices,
        blank=False,
        null=False,
    )
    key_size = models.PositiveIntegerField(
        verbose_name=_("Key Size"),
        blank=True,
        null=True,
    )

    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_dnssec_keys",
        blank=True,
        null=True,
    )

    clone_fields = (
        "description",
        "type",
        "lifetime",
        "algorithm",
        "key_size",
        "tenant",
    )

    class Meta:
        verbose_name = _("DNSSEC Key")
        verbose_name_plural = _("DNSSEC Keys")
        unique_together = (
            "name",
            "type",
        )

        ordering = ("name",)

    def __str__(self):
        return f"{str(self.name)} [{self.type}]"

    # TODO: Remove in version 1.3.0 (NetBox #18555)
    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:dnsseckey", kwargs={"pk": self.pk})

    def get_type_color(self):
        return DNSSECKeyTypeChoices.colors.get(self.type)


@register_search
class DNSSECKeyIndex(SearchIndex):
    model = DNSSECKey
    fields = (
        ("name", 100),
        ("description", 500),
    )
