import dns
from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import models
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
    class Meta:
        verbose_name = _("Record Template")
        verbose_name_plural = _("Record Templates")

        ordering = ("name",)

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

    def __str__(self):
        return str(self.name)

    name = models.CharField(
        verbose_name=_("Template Name"),
        unique=True,
        max_length=200,
        db_collation="natural_sort",
    )
    record_name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        db_collation="natural_sort",
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

    def get_status_color(self):
        return RecordStatusChoices.colors.get(self.status)

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
                )

    def validate_value(self):
        try:
            validate_record_value(self)
        except ValidationError as exc:
            raise ValidationError({"value": exc})

    def matching_records(self, zone):
        return zone.records.filter(
            name=self.record_name, type=self.type, value=self.value
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
                {
                    None: _(
                        "Error while processing record template {template}: {error}"
                    ).format(template=self, error=exc.messages[0])
                }
            )

        if tags := self.tags.all():
            record.tags.set(tags)

    def clean_fields(self, exclude=None):
        self.type = self.type.upper()
        if get_plugin_config("netbox_dns", "convert_names_to_lowercase", False):
            self.record_name = self.record_name.lower()

        super().clean_fields(exclude=exclude)

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
