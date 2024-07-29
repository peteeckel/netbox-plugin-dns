from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search


__all__ = (
    "ZoneTemplate",
    "ZoneTemplateIndex",
)


class ZoneTemplate(NetBoxModel):
    name = models.CharField(
        verbose_name="Template name",
        unique=True,
        max_length=200,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    nameservers = models.ManyToManyField(
        to="NameServer",
        related_name="+",
        blank=True,
    )
    record_templates = models.ManyToManyField(
        to="RecordTemplate",
        related_name="zone_templates",
        blank=True,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )
    registrar = models.ForeignKey(
        to="Registrar",
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="The external registrar the domain is registered with",
        blank=True,
        null=True,
    )
    registrant = models.ForeignKey(
        to="Contact",
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="The owner of the domain",
        blank=True,
        null=True,
    )
    admin_c = models.ForeignKey(
        to="Contact",
        on_delete=models.SET_NULL,
        verbose_name="Admin contact",
        related_name="+",
        help_text="The administrative contact for the domain",
        blank=True,
        null=True,
    )
    tech_c = models.ForeignKey(
        to="Contact",
        on_delete=models.SET_NULL,
        verbose_name="Tech contact",
        related_name="+",
        help_text="The technical contact for the domain",
        blank=True,
        null=True,
    )
    billing_c = models.ForeignKey(
        to="Contact",
        on_delete=models.SET_NULL,
        verbose_name="Billing contact",
        related_name="+",
        help_text="The billing contact for the domain",
        blank=True,
        null=True,
    )

    clone_fields = [
        "description",
        "nameservers",
        "record_templates",
        "tenant",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    ]

    template_fields = [
        "tenant",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    ]

    class Meta:
        ordering = ["name"]

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
