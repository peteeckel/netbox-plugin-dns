from dns import name as dns_name
from dns.exception import DNSException

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search

from netbox_dns.validators import validate_rname


__all__ = (
    "ZoneTemplate",
    "ZoneTemplateIndex",
)


class ZoneTemplate(NetBoxModel):
    class Meta:
        verbose_name = _("Zone Template")
        verbose_name_plural = _("Zone Templates")

        ordering = ("name",)

    clone_fields = (
        "description",
        "nameservers",
        "record_templates",
        "soa_mname",
        "soa_rname",
        "dnssec_policy",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
        "tenant",
    )

    template_fields = (
        "soa_mname",
        "soa_rname",
        "dnssec_policy",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
        "tenant",
    )

    def __str__(self):
        return str(self.name)

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
    soa_mname = models.ForeignKey(
        verbose_name=_("SOA MName"),
        to="NameServer",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    soa_rname = models.CharField(
        verbose_name=_("SOA RName"),
        max_length=255,
        blank=True,
    )
    record_templates = models.ManyToManyField(
        verbose_name=_("Record Templates"),
        to="RecordTemplate",
        related_name="zone_templates",
        blank=True,
    )
    dnssec_policy = models.ForeignKey(
        verbose_name=_("DNSSEC Policy"),
        to="DNSSECPolicy",
        on_delete=models.SET_NULL,
        related_name="zone_templates",
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
    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
    )

    def apply_to_zone_data(self, data):
        fields_changed = False
        for field in self.template_fields:
            if data.get(field) in (None, "") and getattr(self, field) not in (None, ""):
                fields_changed = True
                data[field] = getattr(self, field)

        return fields_changed

    def apply_to_zone_relations(self, zone):
        if not zone.nameservers.all() and self.nameservers.all():
            zone.nameservers.set(self.nameservers.all())

        if not zone.tags.all() and self.tags.all():
            zone.tags.set(self.tags.all())

        self.create_records(zone)

    def create_records(self, zone):
        for record_template in self.record_templates.all():
            record_template.create_record(zone=zone)

    def clean(self, *args, **kwargs):
        if self.soa_rname:
            try:
                dns_name.from_text(self.soa_rname, origin=dns_name.root)
                validate_rname(self.soa_rname)
            except (DNSException, ValidationError) as exc:
                raise ValidationError(
                    {
                        "soa_rname": exc,
                    }
                )


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
