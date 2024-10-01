from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.models.features import ContactsMixin

from netbox_dns.utilities import (
    name_to_unicode,
    normalize_name,
    NameFormatError,
)
from netbox_dns.choices import RecordTypeChoices
from netbox_dns.validators import validate_fqdn
from netbox_dns.mixins import ObjectModificationMixin

from .record import Record


__all__ = (
    "NameServer",
    "NameServerIndex",
)


class NameServer(ObjectModificationMixin, ContactsMixin, NetBoxModel):
    name = models.CharField(
        verbose_name=_("Name"),
        unique=True,
        max_length=255,
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=200,
        blank=True,
    )
    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_nameservers",
        blank=True,
        null=True,
    )

    clone_fields = (
        "name",
        "description",
    )

    class Meta:
        verbose_name = _("Nameserver")
        verbose_name_plural = _("Nameservers")

        ordering = ("name",)

    def __str__(self):
        try:
            return dns_name.from_text(self.name, origin=None).to_unicode()
        except dns_name.IDNAException:
            return self.name

    @property
    def display_name(self):
        return name_to_unicode(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:nameserver", kwargs={"pk": self.pk})

    def clean(self, *args, **kwargs):
        try:
            self.name = normalize_name(self.name)
        except NameFormatError as exc:
            raise ValidationError(
                {
                    "name": str(exc),
                }
            ) from None

        try:
            validate_fqdn(self.name)
        except ValidationError as exc:
            raise ValidationError(
                {
                    "name": exc,
                }
            ) from None

        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        changed_fields = self.changed_fields

        with transaction.atomic():
            super().save(*args, **kwargs)

            if changed_fields is not None and "name" in changed_fields:
                soa_zones = self.zones_soa.all()
                for soa_zone in soa_zones:
                    soa_zone.update_soa_record()

                zones = self.zones.all()
                for zone in zones:
                    zone.update_ns_records()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            zones = self.zones.all()
            for zone in zones:
                Record.objects.filter(
                    Q(zone=zone),
                    Q(managed=True),
                    Q(value=f"{self.name}."),
                    Q(type=RecordTypeChoices.NS),
                ).delete()

            super().delete(*args, **kwargs)


@register_search
class NameServerIndex(SearchIndex):
    model = NameServer
    fields = (
        ("name", 100),
        ("description", 500),
    )
