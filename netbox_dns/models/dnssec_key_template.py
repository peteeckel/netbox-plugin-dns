from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.models.features import ContactsMixin

from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)
from netbox_dns.validators import validate_key_template


__all__ = (
    "DNSSECKeyTemplate",
    "DNSSECKeyTemplateIndex",
)


class DNSSECKeyTemplate(ContactsMixin, NetBoxModel):
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
        choices=DNSSECKeyTemplateTypeChoices,
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
        choices=DNSSECKeyTemplateAlgorithmChoices,
        blank=False,
        null=False,
    )
    key_size = models.PositiveIntegerField(
        verbose_name=_("Key Size"),
        choices=DNSSECKeyTemplateKeySizeChoices,
        blank=True,
        null=True,
    )

    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_dnssec_key_templates",
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
        verbose_name = _("DNSSEC Key Template")
        verbose_name_plural = _("DNSSEC Key Templates")
        unique_together = (
            "name",
            "type",
        )

        ordering = ("name",)

    def __str__(self):
        return f"{str(self.name)} [{self.type}]"

    # TODO: Remove in version 1.3.0 (NetBox #18555)
    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:dnsseckeytemplate", kwargs={"pk": self.pk})

    def get_type_color(self):
        return DNSSECKeyTemplateTypeChoices.colors.get(self.type)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        validate_key_template(self)

    def save(self, *args, **kwargs):
        validate_key_template(self)

        super().save(*args, **kwargs)


@register_search
class DNSSECKeyTemplateIndex(SearchIndex):
    model = DNSSECKeyTemplate
    fields = (
        ("name", 100),
        ("description", 500),
    )
