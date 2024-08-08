import ipaddress

import dns
from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.db.models import Q, ExpressionWrapper, BooleanField, Min
from django.urls import reverse
from django.conf import settings

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.plugins.utils import get_plugin_config
from utilities.querysets import RestrictedQuerySet

from netbox_dns.fields import AddressField
from netbox_dns.utilities import arpa_to_prefix, name_to_unicode
from netbox_dns.validators import validate_generic_name, validate_record_value
from netbox_dns.mixins import ObjectModificationMixin
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices

# +
# This is a hack designed to break cyclic imports between Record and Zone
# -
from netbox_dns.models import zone


__all__ = (
    "Record",
    "RecordIndex",
)


def min_ttl(*ttl_list):
    return min((ttl for ttl in ttl_list if ttl is not None), default=None)


def record_data_from_ip_address(ip_address, zone):
    cf_data = ip_address.custom_field_data

    if cf_data.get("ipaddress_dns_disabled"):
        return None

    data = {
        "name": (
            dns_name.from_text(ip_address.dns_name)
            .relativize(dns_name.from_text(zone.name))
            .to_text()
        ),
        "type": (
            RecordTypeChoices.A
            if ip_address.address.version == 4
            else RecordTypeChoices.AAAA
        ),
        "value": str(ip_address.address.ip),
        "status": (
            RecordStatusChoices.STATUS_ACTIVE
            if ip_address.status
            in settings.PLUGINS_CONFIG["netbox_dns"].get(
                "autodns_ipaddress_active_status", []
            )
            else RecordStatusChoices.STATUS_INACTIVE
        ),
    }

    if "ipaddress_dns_record_ttl" in cf_data:
        data["ttl"] = cf_data.get("ipaddress_dns_record_ttl")

    if (disable_ptr := cf_data.get("ipaddress_dns_record_disable_ptr")) is not None:
        data["disable_ptr"] = disable_ptr

    return data


class RecordManager(models.Manager.from_queryset(RestrictedQuerySet)):
    """
    Custom manager for records providing the activity status annotation
    """

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


class Record(ObjectModificationMixin, NetBoxModel):
    ACTIVE_STATUS_LIST = (RecordStatusChoices.STATUS_ACTIVE,)

    unique_ptr_qs = Q(
        Q(disable_ptr=False),
        Q(Q(type=RecordTypeChoices.A) | Q(type=RecordTypeChoices.AAAA)),
    )

    name = models.CharField(
        max_length=255,
    )
    zone = models.ForeignKey(
        "Zone",
        on_delete=models.CASCADE,
    )
    fqdn = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None,
    )
    type = models.CharField(
        choices=RecordTypeChoices,
        max_length=10,
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
            fqdn = dns_name.from_text(
                self.name, origin=dns_name.from_text(self.zone.name)
            ).relativize(dns_name.root)
            name = fqdn.to_unicode()
        except dns_name.IDNAException:
            name = fqdn.to_text()
        except dns_name.LabelTooLong:
            name = f"{self.name[:59]}..."

        return f"{name} [{self.type}]"

    @property
    def display_name(self):
        return name_to_unicode(self.name)

    def get_status_color(self):
        return RecordStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:record", kwargs={"pk": self.pk})

    @property
    def value_fqdn(self):
        if self.type != RecordTypeChoices.CNAME:
            return None

        _zone = dns_name.from_text(self.zone.name)
        value_fqdn = dns_name.from_text(self.value, origin=_zone)

        return value_fqdn.to_text()

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

        return None

    @property
    def ptr_zone(self):
        if self.type == RecordTypeChoices.A:
            ptr_zone = (
                zone.Zone.objects.filter(
                    view=self.zone.view,
                    rfc2317_prefix__net_contains=self.value,
                )
                .order_by("rfc2317_prefix__net_mask_length")
                .last()
            )

            if ptr_zone is not None:
                return ptr_zone

        ptr_zone = (
            zone.Zone.objects.filter(
                view=self.zone.view, arpa_network__net_contains=self.value
            )
            .order_by("arpa_network__net_mask_length")
            .last()
        )

        return ptr_zone

    def update_ptr_record(self, update_rfc2317_cname=True, save_zone_serial=True):
        ptr_zone = self.ptr_zone

        if (
            ptr_zone is None
            or self.disable_ptr
            or not self.is_active
            or self.name.startswith("*")
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
                ptr_record.rfc2317_cname_record.delete(
                    save_zone_serial=save_zone_serial
                )

        with transaction.atomic():
            if ptr_record is not None:
                if ptr_record.zone.pk != ptr_zone.pk:
                    if ptr_record.rfc2317_cname_record is not None:
                        ptr_record.rfc2317_cname_record.delete()
                    ptr_record.delete(save_zone_serial=save_zone_serial)
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
                        ptr_record.save(save_zone_serial=save_zone_serial)

            if ptr_record is None:
                ptr_record = Record(
                    zone_id=ptr_zone.pk,
                    type=RecordTypeChoices.PTR,
                    name=ptr_name,
                    ttl=self.ttl,
                    value=ptr_value,
                    managed=True,
                )
                ptr_record.save(
                    update_rfc2317_cname=update_rfc2317_cname,
                    save_zone_serial=save_zone_serial,
                )

        self.ptr_record = ptr_record

    def remove_from_rfc2317_cname_record(self, save_zone_serial=True):
        if self.rfc2317_cname_record.pk:
            rfc2317_ptr_records = self.rfc2317_cname_record.rfc2317_ptr_records.exclude(
                pk=self.pk
            )

            if rfc2317_ptr_records:
                self.rfc2317_cname_record.ttl = rfc2317_ptr_records.aggregate(
                    Min("ttl")
                ).get("ttl__min")
                self.rfc2317_cname_record.save(
                    update_fields=["ttl"], save_zone_serial=save_zone_serial
                )
            else:
                self.rfc2317_cname_record.delete()

    def update_rfc2317_cname_record(self, save_zone_serial=True):
        if self.zone.rfc2317_parent_managed:
            cname_name = dns_name.from_text(
                ipaddress.ip_address(self.ip_address).reverse_pointer
            ).relativize(dns_name.from_text(self.zone.rfc2317_parent_zone.name))

            if self.rfc2317_cname_record is not None:
                if self.rfc2317_cname_record.name == cname_name.to_text():
                    self.rfc2317_cname_record.zone = self.zone.rfc2317_parent_zone
                    self.rfc2317_cname_record.value = self.fqdn
                    self.rfc2317_cname_record.ttl = min_ttl(
                        self.rfc2317_cname_record.rfc2317_ptr_records.exclude(
                            pk=self.pk
                        )
                        .aggregate(Min("ttl"))
                        .get("ttl__min"),
                        self.ttl,
                    )
                    self.rfc2317_cname_record.save(save_zone_serial=save_zone_serial)

                    return

                self.remove_from_rfc2317_cname_record(save_zone_serial=save_zone_serial)

            rfc2317_cname_record = Record.objects.filter(
                name=cname_name,
                type=RecordTypeChoices.CNAME,
                zone=self.zone.rfc2317_parent_zone,
                managed=True,
                value=self.fqdn,
            ).first()

            if rfc2317_cname_record is not None:
                rfc2317_cname_record.ttl = min_ttl(
                    rfc2317_cname_record.rfc2317_ptr_records.exclude(pk=self.pk)
                    .aggregate(Min("ttl"))
                    .get("ttl__min"),
                    self.ttl,
                )
                rfc2317_cname_record.save(
                    update_fields=["ttl"], save_zone_serial=save_zone_serial
                )

            else:
                rfc2317_cname_record = Record(
                    name=cname_name,
                    type=RecordTypeChoices.CNAME,
                    zone=self.zone.rfc2317_parent_zone,
                    managed=True,
                    value=self.fqdn,
                    ttl=self.ttl,
                )
                rfc2317_cname_record.save(save_zone_serial=save_zone_serial)

            self.rfc2317_cname_record = rfc2317_cname_record

        else:
            if self.rfc2317_cname_record is not None:
                self.rfc2317_cname_record.delete(save_zone_serial=save_zone_serial)
                self.rfc2317_cname_record = None

    def update_from_ip_address(self, ip_address, zone=None):
        if zone is None:
            zone = self.zone

        data = record_data_from_ip_address(ip_address, zone)

        if data is None:
            self.delete()
            return

        if all((getattr(self, attr) == data[attr] for attr in data.keys())):
            return

        for attr, value in data.items():
            setattr(self, attr, value)

        return self

    @classmethod
    def create_from_ip_address(cls, ip_address, zone):
        data = record_data_from_ip_address(ip_address, zone)

        if data is None:
            return

        return Record(
            zone=zone,
            managed=True,
            ipam_ip_address=ip_address,
            **data,
        )

    def validate_name(self, new_zone=None):
        if new_zone is None:
            new_zone = self.zone

        try:
            _zone = dns_name.from_text(new_zone.name, origin=dns_name.root)
            name = dns_name.from_text(self.name, origin=None)
            fqdn = dns_name.from_text(self.name, origin=_zone)

            _zone.to_unicode()
            name.to_unicode()

            self.name = name.relativize(_zone).to_text()
            self.fqdn = fqdn.to_text()

        except dns.exception.DNSException as exc:
            raise ValidationError(
                {
                    "name": str(exc),
                }
            )

        if not fqdn.is_subdomain(_zone):
            raise ValidationError(
                {
                    "name": f"{self.name} is not a name in {new_zone.name}",
                }
            )

        if self.type not in get_plugin_config(
            "netbox_dns", "tolerate_non_rfc1035_types", default=[]
        ):
            try:
                validate_generic_name(
                    self.name,
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
                        "name": exc,
                    }
                ) from None

    def validate_value(self):
        try:
            validate_record_value(self.type, self.value)
        except ValidationError as exc:
            raise ValidationError({"value": exc}) from None

    def check_unique_record(self, new_zone=None):
        if not get_plugin_config("netbox_dns", "enforce_unique_records", False):
            return

        if not self.is_active:
            return

        if new_zone is None:
            new_zone = self.zone

        records = Record.objects.filter(
            zone=new_zone,
            name=self.name,
            type=self.type,
            value=self.value,
            status__in=Record.ACTIVE_STATUS_LIST,
        )

        if self.pk is not None:
            records = records.exclude(pk=self.pk)

        if records.exists():
            if self.ipam_ip_address is not None:
                if not records.filter(
                    ipam_ip_address__isnull=True
                ).exists() or get_plugin_config(
                    "netbox_dns", "autodns_conflict_deactivate", False
                ):
                    return

            raise ValidationError(
                {
                    "value": f"There is already an active {self.type} record for name {self.name} in zone {self.zone} with value {self.value}."
                }
            ) from None

    def handle_conflicting_address_records(self):
        if self.ipam_ip_address is None or not self.is_active:
            return

        if not get_plugin_config("netbox_dns", "autodns_conflict_deactivate", False):
            return

        records = Record.objects.filter(
            zone=self.zone,
            name=self.name,
            type=self.type,
            value=self.value,
            status__in=Record.ACTIVE_STATUS_LIST,
            ipam_ip_address__isnull=True,
        )

        for record in records:
            record.status = RecordStatusChoices.STATUS_INACTIVE
            record.save(update_fields=["status"])

    def check_unique_rrset_ttl(self):
        if self.pk is not None:
            return

        if not get_plugin_config("netbox_dns", "enforce_unique_rrset_ttl", False):
            return

        if self.type == RecordTypeChoices.PTR and self.managed:
            return

        records = (
            Record.objects.filter(
                zone=self.zone,
                name=self.name,
                type=self.type,
            )
            .exclude(ttl=self.ttl)
            .exclude(type=RecordTypeChoices.PTR, managed=True)
            .exclude(status=RecordStatusChoices.STATUS_INACTIVE)
        )

        if self.ipam_ip_address is not None:
            records = records.exclude(ipam_ip_address__isnull=False)

        if not records.exists():
            return

        conflicting_ttls = ", ".join(set(str(record.ttl) for record in records))
        raise ValidationError(
            {
                "ttl": f"There is at least one active {self.type} record for name {self.name} in zone {self.zone} and TTL is different ({conflicting_ttls})."
            }
        ) from None

    def update_rrset_ttl(self, ttl=None):
        if self.pk is None:
            return

        if not get_plugin_config("netbox_dns", "enforce_unique_rrset_ttl", False):
            return

        if self.type == RecordTypeChoices.PTR and self.managed:
            return

        if ttl is None:
            ttl = self.ttl

        records = (
            Record.objects.filter(
                zone=self.zone,
                name=self.name,
                type=self.type,
            )
            .exclude(pk=self.pk)
            .exclude(ttl=ttl)
            .exclude(type=RecordTypeChoices.PTR, managed=True)
            .exclude(status=RecordStatusChoices.STATUS_INACTIVE)
        )

        for record in records:
            record.ttl = ttl
            record.save(update_fields=["ttl"], update_rrset_ttl=False)

    def clean_fields(self, *args, **kwargs):
        self.type = self.type.upper()
        super().clean_fields(*args, **kwargs)

    def clean(self, *args, new_zone=None, **kwargs):
        self.validate_name(new_zone=new_zone)
        self.validate_value()
        self.check_unique_record(new_zone=new_zone)
        if self.pk is None:
            self.check_unique_rrset_ttl()

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

        if self.type == RecordTypeChoices.SOA and self.name != "@":
            raise ValidationError(
                {
                    "name": "SOA records are only allowed with name @ and are created automatically by NetBox DNS"
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

        super().clean(*args, **kwargs)

    def save(
        self,
        *args,
        update_rfc2317_cname=True,
        save_zone_serial=True,
        update_rrset_ttl=True,
        **kwargs,
    ):
        self.full_clean()

        if self.pk is not None and update_rrset_ttl:
            self.update_rrset_ttl()

        if self.is_ptr_record:
            if self.zone.is_rfc2317_zone:
                self.ip_address = self.address_from_rfc2317_name
                if update_rfc2317_cname:
                    self.update_rfc2317_cname_record(save_zone_serial=save_zone_serial)
            else:
                self.ip_address = self.address_from_name

        elif self.is_address_record:
            self.ip_address = self.value
        else:
            self.ip_address = None

        if self.is_address_record:
            self.handle_conflicting_address_records()
            self.update_ptr_record(
                update_rfc2317_cname=update_rfc2317_cname,
                save_zone_serial=save_zone_serial,
            )
        elif self.ptr_record is not None:
            self.ptr_record.delete()
            self.ptr_record = None

        changed_fields = self.changed_fields
        if changed_fields is None or changed_fields:
            super().save(*args, **kwargs)

        _zone = self.zone
        if self.type != RecordTypeChoices.SOA and _zone.soa_serial_auto:
            _zone.update_serial(save_zone_serial=save_zone_serial)

    def delete(self, *args, save_zone_serial=True, **kwargs):
        if self.rfc2317_cname_record:
            self.remove_from_rfc2317_cname_record(save_zone_serial=save_zone_serial)

        if self.ptr_record:
            self.ptr_record.delete()

        super().delete(*args, **kwargs)

        _zone = self.zone
        if _zone.soa_serial_auto:
            _zone.update_serial(save_zone_serial=save_zone_serial)


@register_search
class RecordIndex(SearchIndex):
    model = Record
    fields = (
        ("fqdn", 100),
        ("name", 120),
        ("value", 150),
        ("zone", 200),
        ("type", 200),
    )
