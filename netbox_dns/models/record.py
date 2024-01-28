import ipaddress

import dns
from dns import rdata, rdatatype, rdataclass
from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.db.models import Q, ExpressionWrapper, BooleanField
from django.db.models.functions import Length
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from utilities.querysets import RestrictedQuerySet
from utilities.choices import ChoiceSet

try:
    # NetBox 3.5.0 - 3.5.7, 3.5.9+
    from extras.plugins import get_plugin_config
except ImportError:
    # NetBox 3.5.8
    from extras.plugins.utils import get_plugin_config

from netbox_dns.fields import AddressField
from netbox_dns.utilities import (
    arpa_to_prefix,
    name_to_unicode,
)
from netbox_dns.validators import (
    validate_fqdn,
    validate_extended_hostname,
)

# +
# This is a hack designed to break cyclic imports between Record and Zone
# -
import netbox_dns.models.zone as zone


class RecordManager(models.Manager.from_queryset(RestrictedQuerySet)):
    """Special Manager for records providing the activity status annotation"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                active=ExpressionWrapper(
                    Q(
                        Q(zone__status__in=zone.Zone.ACTIVE_STATUS_LIST)
                        & Q(
                            Q(address_record__isnull=True)
                            | Q(
                                address_record__zone__status__in=zone.Zone.ACTIVE_STATUS_LIST
                            )
                        )
                        & Q(status__in=Record.ACTIVE_STATUS_LIST)
                    ),
                    output_field=BooleanField(),
                )
            )
        )


def initialize_choice_names(cls):
    for choice in cls.CHOICES:
        setattr(cls, choice[0], choice[0])
    return cls


@initialize_choice_names
class RecordTypeChoices(ChoiceSet):
    CHOICES = [
        (rdtype.name, rdtype.name)
        for rdtype in sorted(rdatatype.RdataType, key=lambda a: a.name)
        if not rdatatype.is_metatype(rdtype)
    ]
    SINGLETONS = [
        rdtype.name for rdtype in rdatatype.RdataType if rdatatype.is_singleton(rdtype)
    ]


@initialize_choice_names
class RecordClassChoices(ChoiceSet):
    CHOICES = [
        (rdclass.name, rdclass.name)
        for rdclass in sorted(rdataclass.RdataClass)
        if not rdataclass.is_metaclass(rdclass)
    ]


class RecordStatusChoices(ChoiceSet):
    key = "Record.status"

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    CHOICES = [
        (STATUS_ACTIVE, "Active", "blue"),
        (STATUS_INACTIVE, "Inactive", "red"),
    ]


class Record(NetBoxModel):
    ACTIVE_STATUS_LIST = (RecordStatusChoices.STATUS_ACTIVE,)

    unique_ptr_qs = Q(
        Q(disable_ptr=False),
        Q(Q(type=RecordTypeChoices.A) | Q(type=RecordTypeChoices.AAAA)),
    )

    zone = models.ForeignKey(
        "Zone",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        choices=RecordTypeChoices,
        max_length=10,
    )
    name = models.CharField(
        max_length=255,
    )
    value = models.CharField(
        max_length=65535,
    )
    status = models.CharField(
        max_length=50,
        choices=RecordStatusChoices,
        default=RecordStatusChoices.STATUS_ACTIVE,
        blank=False,
    )
    ttl = models.PositiveIntegerField(
        verbose_name="TTL",
        null=True,
        blank=True,
    )
    managed = models.BooleanField(
        null=False,
        default=False,
    )
    ptr_record = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        related_name="address_record",
        verbose_name="PTR record",
        null=True,
        blank=True,
    )
    disable_ptr = models.BooleanField(
        verbose_name="Disable PTR",
        help_text="Disable PTR record creation",
        default=False,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_records",
        blank=True,
        null=True,
    )
    ip_address = AddressField(
        verbose_name="Related IP Address",
        help_text="IP address related to an address (A/AAAA) or PTR record",
        blank=True,
        null=True,
    )
    ipam_ip_address = models.ForeignKey(
        verbose_name="IPAM IP Address",
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="netbox_dns_records",
        blank=True,
        null=True,
    )
    rfc2317_cname_record = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="rfc2317_ptr_records",
        verbose_name="RFC2317 CNAME record",
        null=True,
        blank=True,
    )

    objects = RecordManager()
    raw_objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        "zone",
        "type",
        "name",
        "value",
        "status",
        "ttl",
        "disable_ptr",
        "description",
    ]

    class Meta:
        ordering = ("zone", "name", "type", "value", "status")

    def __str__(self):
        try:
            name = (
                dns_name.from_text(
                    self.name, origin=dns_name.from_text(self.zone.name, origin=None)
                )
                .relativize(dns_name.root)
                .to_unicode()
            )
        except dns_name.IDNAException:
            name = self.name
        except dns_name.LabelTooLong as exc:
            name = f"{self.name[:59]}..."

        return f"{name} [{self.type}]"

    @property
    def display_name(self):
        return name_to_unicode(self.name)

    def get_status_color(self):
        return RecordStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:record", kwargs={"pk": self.id})

    @property
    def fqdn(self):
        zone = dns_name.from_text(self.zone.name)
        name = dns_name.from_text(self.name, origin=zone)

        return name.to_text()

    @property
    def address_from_name(self):
        prefix = arpa_to_prefix(self.fqdn)
        if prefix is not None:
            return prefix.ip

        return None

    @property
    def address_from_rfc2317_name(self):
        prefix = self.zone.rfc2317_prefix
        if prefix is not None:
            return ".".join(str(prefix.ip).split(".")[0:3] + [self.name])

        return None

    @property
    def is_active(self):
        return (
            self.status in Record.ACTIVE_STATUS_LIST
            and self.zone.status in zone.Zone.ACTIVE_STATUS_LIST
        )

    @property
    def is_address_record(self):
        return self.type in (RecordTypeChoices.A, RecordTypeChoices.AAAA)

    @property
    def is_ptr_record(self):
        return self.type == RecordTypeChoices.PTR

    @property
    def rfc2317_ptr_name(self):
        return self.value.split(".")[-1]

    @property
    def rfc2317_ptr_cname_name(self):
        assert self.type == RecordTypeChoices.A
        if (
            self.ptr_record is not None
            and self.ptr_record.zone.rfc2317_parent_zone is not None
        ):
            return dns_name.from_text(
                ipaddress.ip_address(self.value).reverse_pointer
            ).relativize(
                dns_name.from_text(self.ptr_record.zone.rfc2317_parent_zone.name)
            )

    @property
    def ptr_zone(self):
        if self.type == RecordTypeChoices.A:
            ptr_zone = (
                zone.Zone.objects.filter(
                    self.zone.view_filter,
                    rfc2317_prefix__net_contains=self.value,
                )
                .order_by("rfc2317_prefix__net_mask_length")
                .last()
            )

            if ptr_zone is not None:
                return ptr_zone

        ptr_zone = (
            zone.Zone.objects.filter(
                self.zone.view_filter, arpa_network__net_contains=self.value
            )
            .order_by("arpa_network__net_mask_length")
            .last()
        )

        return ptr_zone

    def update_ptr_record(self):
        ptr_zone = self.ptr_zone

        if (
            ptr_zone is None
            or self.disable_ptr
            or not self.is_active
            or self.name == "*"
        ):
            if self.ptr_record is not None:
                with transaction.atomic():
                    self.ptr_record.delete()
                    self.ptr_record = None
            return

        if ptr_zone.is_rfc2317_zone:
            ptr_name = self.rfc2317_ptr_name
        else:
            ptr_name = dns_name.from_text(
                ipaddress.ip_address(self.value).reverse_pointer
            ).relativize(dns_name.from_text(ptr_zone.name))

        ptr_value = self.fqdn
        ptr_record = self.ptr_record

        if ptr_record is not None:
            if (
                not ptr_record.zone.is_rfc2317_zone
                and ptr_record.rfc2317_cname_record is not None
            ):
                ptr_record.rfc2317_cname_record.delete()

        with transaction.atomic():
            if ptr_record is not None:
                if ptr_record.zone.pk != ptr_zone.pk:
                    ptr_record.delete()
                    ptr_record = None

                else:
                    if (
                        ptr_record.name != ptr_name
                        or ptr_record.value != ptr_value
                        or ptr_record.ttl != self.ttl
                    ):
                        ptr_record.name = ptr_name
                        ptr_record.value = ptr_value
                        ptr_record.ttl = self.ttl
                        ptr_record.save()

            if ptr_record is None:
                ptr_record = Record.objects.create(
                    zone_id=ptr_zone.pk,
                    type=RecordTypeChoices.PTR,
                    name=ptr_name,
                    ttl=self.ttl,
                    value=ptr_value,
                    managed=True,
                )

        self.ptr_record = ptr_record
        if self.pk:
            super().save()

    def update_rfc2317_cname_record(self):
        if self.zone.rfc2317_parent_managed:
            cname_name = dns_name.from_text(
                ipaddress.ip_address(self.ip_address).reverse_pointer
            ).relativize(dns_name.from_text(self.zone.rfc2317_parent_zone.name))

            if self.rfc2317_cname_record is not None:
                self.rfc2317_cname_record.name = cname_name
                self.rfc2317_cname_record.zone = self.zone.rfc2317_parent_zone
                self.rfc2317_cname_record.value = self.fqdn
                self.rfc2317_cname_record.save()
            else:
                rfc2317_cname_record = Record.objects.filter(
                    name=cname_name,
                    type=RecordTypeChoices.CNAME,
                    zone=self.zone.rfc2317_parent_zone,
                    managed=True,
                    value=self.fqdn,
                ).first()
                if rfc2317_cname_record is None:
                    rfc2317_cname_record = Record.objects.create(
                        name=cname_name,
                        type=RecordTypeChoices.CNAME,
                        zone=self.zone.rfc2317_parent_zone,
                        managed=True,
                        value=self.fqdn,
                    )

                self.rfc2317_cname_record = rfc2317_cname_record

        else:
            if self.rfc2317_cname_record is not None:
                self.rfc2317_cname_record.delete()
                self.rfc2317_cname_record = None

    def validate_name(self):
        try:
            zone = dns_name.from_text(self.zone.name, origin=dns_name.root)
            name = dns_name.from_text(self.name, origin=None)
            fqdn = dns_name.from_text(self.name, origin=zone)

            zone.to_unicode()
            name.to_unicode()

            self.name = name.to_text()

        except dns.exception.DNSException as exc:
            raise ValidationError(
                {
                    "name": str(exc),
                }
            )

        if not fqdn.is_subdomain(zone):
            raise ValidationError(
                {
                    "name": f"{self.name} is not a name in {self.zone.name}",
                }
            )

        if self.type not in get_plugin_config(
            "netbox_dns", "tolerate_non_rfc1035_types", default=list()
        ):
            try:
                validate_extended_hostname(
                    self.name,
                    (
                        self.type
                        in get_plugin_config(
                            "netbox_dns",
                            "tolerate_leading_underscore_types",
                            default=list(),
                        )
                    ),
                )
            except ValidationError as exc:
                raise ValidationError(
                    {
                        "name": exc,
                    }
                ) from None

    def validate_value(self):
        if self.type in (RecordTypeChoices.PTR):
            try:
                validate_fqdn(self.value)
            except ValidationError as exc:
                raise ValidationError(
                    {
                        "value": exc,
                    }
                ) from None

        try:
            rdata.from_text(RecordClassChoices.IN, self.type, self.value)
        except dns.exception.SyntaxError as exc:
            raise ValidationError(
                {
                    "value": f"Record value {self.value} is not a valid value for a {self.type} record: {exc}."
                }
            ) from None

    def check_unique(self):
        if not get_plugin_config("netbox_dns", "enforce_unique_records", False):
            return

        if not self.is_active:
            return

        records = Record.objects.filter(
            zone=self.zone,
            name=self.name,
            type=self.type,
            value=self.value,
            status__in=Record.ACTIVE_STATUS_LIST,
        )
        if len(records):
            raise ValidationError(
                {
                    "value": f"There is already an active {self.type} record for name {self.name} in zone {self.zone} with value {self.value}."
                }
            ) from None

    def clean_fields(self, *args, **kwargs):
        self.type = self.type.upper()
        super().clean_fields(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_name()
        self.validate_value()
        self.check_unique()

        if not self.is_active:
            return

        records = Record.objects.filter(
            name=self.name, zone=self.zone, active=True
        ).exclude(pk=self.pk)

        if self.type == RecordTypeChoices.A and not self.disable_ptr:
            ptr_zone = self.ptr_zone

            if (
                ptr_zone is not None
                and ptr_zone.is_rfc2317_zone
                and ptr_zone.rfc2317_parent_managed
            ):
                ptr_cname_zone = ptr_zone.rfc2317_parent_zone
                ptr_cname_name = self.rfc2317_ptr_cname_name
                ptr_fqdn = dns_name.from_text(
                    self.rfc2317_ptr_name, origin=dns_name.from_text(ptr_zone.name)
                )

                if (
                    Record.objects.filter(
                        zone=ptr_cname_zone,
                        name=ptr_cname_name,
                        active=True,
                    )
                    .exclude(
                        type=RecordTypeChoices.CNAME,
                        value=ptr_fqdn,
                    )
                    .exclude(type=RecordTypeChoices.NSEC)
                    .exists()
                ):
                    raise ValidationError(
                        {
                            "value": f"There is already an active record for name {ptr_cname_name} in zone {ptr_cname_zone}, RFC2317 CNAME is not allowed."
                        }
                    ) from None

        if self.type == RecordTypeChoices.CNAME:
            if records.exclude(type=RecordTypeChoices.NSEC).exists():
                raise ValidationError(
                    {
                        "type": f"There is already an active record for name {self.name} in zone {self.zone}, CNAME is not allowed."
                    }
                ) from None

        elif (
            records.filter(type=RecordTypeChoices.CNAME).exists()
            and self.type != RecordTypeChoices.NSEC
        ):
            raise ValidationError(
                {
                    "type": f"There is already an active CNAME record for name {self.name} in zone {self.zone}, no other record allowed."
                }
            ) from None

        elif self.type in RecordTypeChoices.SINGLETONS:
            if records.filter(type=self.type).exists():
                raise ValidationError(
                    {
                        "type": f"There is already an active {self.type} record for name {self.name} in zone {self.zone}, more than one are not allowed."
                    }
                ) from None

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.is_ptr_record:
            if self.zone.is_rfc2317_zone:
                self.ip_address = self.address_from_rfc2317_name
                self.update_rfc2317_cname_record()
            else:
                self.ip_address = self.address_from_name

        elif self.is_address_record:
            self.ip_address = self.value
        else:
            self.ip_address = None

        if self.is_address_record:
            self.update_ptr_record()
        elif self.ptr_record is not None:
            self.ptr_record.delete()
            self.ptr_record = None

        super().save(*args, **kwargs)

        zone = self.zone
        if self.type != RecordTypeChoices.SOA and zone.soa_serial_auto:
            zone.update_serial()

    def delete(self, *args, **kwargs):
        if self.rfc2317_cname_record:
            if self.rfc2317_cname_record.rfc2317_ptr_records.count() == 1:
                self.rfc2317_cname_record.delete()

        if self.ptr_record:
            self.ptr_record.delete()

        super().delete(*args, **kwargs)

        zone = self.zone
        if zone.soa_serial_auto:
            zone.update_serial()


@register_search
class RecordIndex(SearchIndex):
    model = Record
    fields = (
        ("name", 100),
        ("value", 150),
        ("zone", 200),
        ("type", 200),
    )
