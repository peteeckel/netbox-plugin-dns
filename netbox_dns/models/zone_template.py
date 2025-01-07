from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search


__all__ = (
    "ZoneTemplate",
    "ZoneTemplateIndex",
)


class ZoneTemplate(NetBoxModel):
    name = models.CharField(
        verbose_name=_("Template Name"),
        unique=True,
        max_length=200,
        db_collation="natural_sort",
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=200,
        blank=True,
    )
    nameservers = models.ManyToManyField(
        verbose_name=_("Nameservers"),
        to="NameServer",
        related_name="+",
        blank=True,
    )
    record_templates = models.ManyToManyField(
        verbose_name=_("Record Templates"),
        to="RecordTemplate",
        related_name="zone_templates",
        blank=True,
    )
    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    registrar = models.ForeignKey(
        verbose_name=_("Registrar"),
        to="Registrar",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    registrant = models.ForeignKey(
        verbose_name=_("Registrant"),
        to="RegistrationContact",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    admin_c = models.ForeignKey(
        verbose_name=_("Administrative Contact"),
        to="RegistrationContact",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    tech_c = models.ForeignKey(
        verbose_name=_("Technical Contact"),
        to="RegistrationContact",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    billing_c = models.ForeignKey(
        verbose_name=_("Billing Contact"),
        to="RegistrationContact",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )

    clone_fields = (
        "description",
        "nameservers",
        "record_templates",
        "tenant",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    )

    template_fields = (
        "tenant",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    )

    class Meta:
        verbose_name = _("Zone Template")
        verbose_name_plural = "Zone Templates"

        ordering = ("name",)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:zonetemplate", kwargs={"pk": self.pk})

    def apply_to_zone(self, zone):
        if not zone.nameservers.all() and self.nameservers.all():
            zone.nameservers.set(self.nameservers.all())

        if not zone.tags.all() and self.tags.all():
            zone.tags.set(self.tags.all())

        fields_changed = True
        for field in self.template_fields:
            if getattr(zone, field) is None and getattr(self, field) is not None:
                fields_changed = True
                setattr(zone, field, getattr(self, field))

        if fields_changed:
            zone.save()

        self.create_records(zone)

    def create_records(self, zone):
        for record_template in self.record_templates.all():
            record_template.create_record(zone=zone)


@register_search
class ZoneTemplateIndex(SearchIndex):
    model = ZoneTemplate
    fields = (
        ("name", 100),
        ("tenant", 300),
        ("registrar", 300),
        ("registrant", 300),
        ("admin_c", 300),
        ("tech_c", 300),
        ("billing_c", 300),
        ("description", 500),
    )
