import dns
from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.plugins.utils import get_plugin_config

from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices
from netbox_dns.validators import validate_generic_name, validate_record_value

from .record import Record


__all__ = (
    "RecordTemplate",
    "RecordTemplateIndex",
)


class RecordTemplate(NetBoxModel):
    name = models.CharField(
        verbose_name=_("Template Name"),
        unique=True,
        max_length=200,
    )
    record_name = models.CharField(
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
        choices=RecordTypeChoices,
    )
    value = models.CharField(
        verbose_name=_("Value"),
        max_length=65535,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        choices=RecordStatusChoices,
        default=RecordStatusChoices.STATUS_ACTIVE,
        blank=False,
    )
    ttl = models.PositiveIntegerField(
        verbose_name=_("TTL"),
        null=True,
        blank=True,
    )
    disable_ptr = models.BooleanField(
        verbose_name=_("Disable PTR"),
        help_text=_("Disable PTR record creation"),
        default=False,
    )
    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
    )

    clone_fields = (
        "record_name",
        "description",
        "type",
        "value",
        "status",
        "ttl",
        "disable_ptr",
        "tenant",
    )

    template_fields = (
        "type",
        "value",
        "status",
        "ttl",
        "disable_ptr",
        "tenant",
    )

    class Meta:
        verbose_name = _("Record Template")
        verbose_name_plural = _("Record Templates")

        ordering = ("name",)

    def __str__(self):
        return str(self.name)

    def get_status_color(self):
        return RecordStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:recordtemplate", kwargs={"pk": self.pk})

    def validate_name(self):
        try:
            name = dns_name.from_text(self.record_name, origin=None)
            name.to_unicode()

        except dns.exception.DNSException as exc:
            raise ValidationError({"record_name": str(exc)})

        if self.type not in get_plugin_config(
            "netbox_dns", "tolerate_non_rfc1035_types", default=[]
        ):
            try:
                validate_generic_name(
                    self.record_name,
                    (
                        self.type
                        in get_plugin_config(
                            "netbox_dns",
                            "tolerate_leading_underscore_types",
                            default=[],
                        )
                    ),
                )
            except ValidationError as exc:
                raise ValidationError(
                    {
                        "record_name": exc,
                    }
                ) from None

    def validate_value(self):
        try:
            validate_record_value(self)
        except ValidationError as exc:
            raise ValidationError({"value": exc}) from None

    def matching_records(self, zone):
        return Record.objects.filter(
            zone=zone, name=self.record_name, type=self.type, value=self.value
        )

    def create_record(self, zone):
        if self.matching_records(zone).exists():
            return

        record_data = {
            "zone": zone,
            "name": self.record_name,
        }
        for field in self.template_fields:
            record_data[field] = getattr(self, field)

        try:
            record = Record.objects.create(**record_data)
        except ValidationError as exc:
            raise ValidationError(
                _("Error while processing record template {template}: {error}").format(
                    template=self, error=exc.messages[0]
                )
            )

        if tags := self.tags.all():
            record.tags.set(tags)

    def clean_fields(self, *args, **kwargs):
        self.type = self.type.upper()
        super().clean_fields(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_name()
        self.validate_value()

        super().clean(*args, **kwargs)


@register_search
class RecordTemplateIndex(SearchIndex):
    model = RecordTemplate
    fields = (
        ("name", 100),
        ("record_name", 120),
        ("value", 150),
        ("type", 200),
    )
