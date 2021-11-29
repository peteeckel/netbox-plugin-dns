import ipaddress

from math import ceil
from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Q, Max
from django.db.models.functions import Length
from django.urls import reverse

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from extras.utils import extras_features
from netbox.models import PrimaryModel, TaggableManager
from utilities.querysets import RestrictedQuerySet


@extras_features("custom_fields", "custom_links", "export_templates", "webhooks")
class NameServer(PrimaryModel):
    name = models.CharField(
        unique=True,
        max_length=255,
    )
    tags = TaggableManager(
        through="extras.TaggedItem",
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ["name"]

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:nameserver", kwargs={"pk": self.pk})


@extras_features("custom_fields", "custom_links", "export_templates", "webhooks")
class Zone(PrimaryModel):
    STATUS_ACTIVE = "active"
    STATUS_PASSIVE = "passive"

    CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_PASSIVE, "Passive"),
    )

    CSS_CLASSES = {
        STATUS_PASSIVE: "danger",
        STATUS_ACTIVE: "success",
    }

    name = models.CharField(
        unique=True,
        max_length=255,
    )
    status = models.CharField(
        max_length=50,
        choices=CHOICES,
        default=STATUS_ACTIVE,
        blank=True,
    )
    nameservers = models.ManyToManyField(
        NameServer,
        related_name="zones",
        blank=True,
    )
    tags = TaggableManager(
        through="extras.TaggedItem",
        blank=True,
    )
    default_ttl = models.PositiveIntegerField(
        blank=True,
        verbose_name="Default TTL",
        validators=[MinValueValidator(1)],
    )
    soa_ttl = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name="SOA TTL",
        validators=[MinValueValidator(1)],
    )
    soa_mname = models.ForeignKey(
        NameServer,
        related_name="zones_soa",
        verbose_name="SOA MName",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    soa_rname = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name="SOA RName",
    )
    soa_serial = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="SOA Serial",
        validators=[MinValueValidator(1), MaxValueValidator(4294967295)],
    )
    soa_refresh = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name="SOA Refresh",
        validators=[MinValueValidator(1)],
    )
    soa_retry = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name="SOA Retry",
        validators=[MinValueValidator(1)],
    )
    soa_expire = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name="SOA Expire",
        validators=[MinValueValidator(1)],
    )
    soa_minimum = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name="SOA Minimum TTL",
        validators=[MinValueValidator(1)],
    )
    soa_serial_auto = models.BooleanField(
        verbose_name="Generate SOA Serial",
        help_text="Automatically generate the SOA Serial field",
        default=True,
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        "name",
        "status",
        "nameservers",
        "default_ttl",
        "soa_ttl",
        "soa_mname",
        "soa_rname",
        "soa_refresh",
        "soa_retry",
        "soa_expire",
        "soa_minimum",
    ]

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:zone", kwargs={"pk": self.pk})

    def get_status_class(self):
        return self.CSS_CLASSES.get(self.status)

    def update_soa_record(self):
        soa_name = "@"
        soa_ttl = self.soa_ttl
        soa_value = (
            f"({self.soa_mname} {self.soa_rname} {self.soa_serial}"
            f" {self.soa_refresh} {self.soa_retry} {self.soa_expire}"
            f" {self.soa_minimum})"
        )

        old_soa_records = self.record_set.filter(type=Record.SOA, name=soa_name)

        if len(old_soa_records):
            for index, record in enumerate(old_soa_records):
                if index > 0:
                    record.delete()
                    continue

                if record.ttl != soa_ttl or record.value != soa_value:
                    record.ttl = soa_ttl
                    record.value = soa_value
                    record.managed = True
                    record.save()
        else:
            Record.objects.create(
                zone_id=self.pk,
                type=Record.SOA,
                name=soa_name,
                ttl=soa_ttl,
                value=soa_value,
                managed=True,
            )

    def get_auto_serial(self):
        records = Record.objects.filter(zone=self).exclude(type=Record.SOA)
        if records:
            soa_serial = (
                records.aggregate(Max("last_updated"))
                .get("last_updated__max")
                .timestamp()
            )
        else:
            soa_serial = ceil(datetime.now().timestamp())

        if self.last_updated:
            soa_serial = ceil(max(soa_serial, self.last_updated.timestamp()))

        return soa_serial

    def update_serial(self):
        self.last_updated = datetime.now()
        self.save()

    def update_ns_records(self, nameservers):
        ns_name = "@"
        ns_ttl = self.default_ttl

        delete_ns = self.record_set.filter(type=Record.NS, managed=True).exclude(
            value__in=nameservers
        )
        for record in delete_ns:
            record.delete()

        for ns in nameservers:
            Record.objects.update_or_create(
                zone_id=self.pk,
                type=Record.NS,
                name=ns_name,
                ttl=ns_ttl,
                value=ns,
                managed=True,
            )

    def check_nameservers(self):
        nameservers = self.nameservers.all()

        ns_warnings = []
        for nameserver in nameservers:
            ns_domain = ".".join(nameserver.name.split(".")[1:])
            if not ns_domain:
                continue

            try:
                ns_zone = Zone.objects.get(name=ns_domain)
            except ObjectDoesNotExist:
                continue

            ns_name = nameserver.name.split(".")[0]
            address_records = Record.objects.filter(
                Q(zone=ns_zone),
                Q(Q(name=f"{nameserver.name}.") | Q(name=ns_name)),
                Q(Q(type=Record.A) | Q(type=Record.AAAA)),
            )

            if not address_records:
                ns_warnings.append(
                    f"Nameserver {nameserver.name} does not have an address record in zone {ns_zone.name}"
                )

        return ns_warnings

    def save(self, *args, **kwargs):
        new_zone = self.pk is None
        if not new_zone:
            renamed_zone = Zone.objects.get(pk=self.pk).name != self.name
        else:
            renamed_zone = False

        if self.soa_serial_auto:
            self.soa_serial = self.get_auto_serial()

        super().save(*args, **kwargs)

        if (new_zone or renamed_zone) and self.name.endswith(".arpa"):
            address_records = Record.objects.filter(
                type__in=(Record.A, Record.AAAA)
            ).exclude(disable_ptr=True)
            for record in address_records:
                record.update_ptr_record()

        elif renamed_zone:
            for record in self.record_set.filter(ptr_record__isnull=False):
                record.update_ptr_record()

        self.update_soa_record()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            address_records = list(self.record_set.filter(ptr_record__isnull=False))
            for record in address_records:
                record.ptr_record.delete()

            ptr_records = self.record_set.filter(address_record__isnull=False)
            deleted_ptr_records = [pk for pk in ptr_records]

            super().delete(*args, **kwargs)

        for record in Record.objects.filter(ptr_record__in=deleted_ptr_records):
            record.update_ptr_record()


@receiver(m2m_changed, sender=Zone.nameservers.through)
def update_ns_records(**kwargs):
    if kwargs.get("action") not in ["post_add", "post_remove"]:
        return

    zone = kwargs.get("instance")
    nameservers = zone.nameservers.all()

    new_nameservers = [f'{ns.name.rstrip(".")}.' for ns in nameservers]

    zone.update_ns_records(new_nameservers)


@extras_features("custom_fields", "custom_links", "export_templates", "webhooks")
class Record(PrimaryModel):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SOA = "SOA"
    SRV = "SRV"
    PTR = "PTR"
    SPF = "SPF"
    CAA = "CAA"
    DS = "DS"
    SSHFP = "SSHFP"
    TLSA = "TLSA"
    AFSDB = "AFSDB"
    APL = "APL"
    DNSKEY = "DNSKEY"
    CDNSKEY = "CDNSKEY"
    CERT = "CERT"
    DCHID = "DCHID"
    DNAME = "DNAME"
    HIP = "HIP"
    IPSECKEY = "IPSECKEY"
    LOC = "LOC"
    NAPTR = "NAPTR"
    NSEC = "NSEC"
    RRSIG = "RRSIG"
    RP = "RP"

    CHOICES = (
        (A, A),
        (AAAA, AAAA),
        (CNAME, CNAME),
        (MX, MX),
        (TXT, TXT),
        (SOA, SOA),
        (NS, NS),
        (SRV, SRV),
        (PTR, PTR),
        (SPF, SPF),
        (CAA, CAA),
        (DS, DS),
        (SSHFP, SSHFP),
        (TLSA, TLSA),
        (AFSDB, AFSDB),
        (APL, APL),
        (DNSKEY, DNSKEY),
        (CDNSKEY, CDNSKEY),
        (CERT, CERT),
        (DCHID, DCHID),
        (DNAME, DNAME),
        (HIP, HIP),
        (IPSECKEY, IPSECKEY),
        (LOC, LOC),
        (NAPTR, NAPTR),
        (NSEC, NSEC),
        (RRSIG, RRSIG),
        (RP, RP),
    )

    unique_ptr_qs = Q(Q(disable_ptr=False), Q(Q(type="A") | Q(type="AAAA")))

    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        choices=CHOICES,
        max_length=10,
    )
    name = models.CharField(
        max_length=255,
    )
    value = models.CharField(
        max_length=1000,
    )
    ttl = models.PositiveIntegerField(
        verbose_name="TTL",
    )
    tags = TaggableManager(
        through="extras.TaggedItem",
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

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ["zone", "type", "name", "value", "ttl", "disable_ptr"]

    class Meta:
        ordering = ("zone", "name", "type", "value")
        constraints = (
            models.UniqueConstraint(
                name="unique_pointer_for_address",
                fields=["type", "value"],
                condition=(
                    models.Q(
                        models.Q(disable_ptr=False),
                        models.Q(type="A") | models.Q(type="AAAA"),
                    )
                ),
            ),
        )

    def __str__(self):
        if self.name.endswith("."):
            return f"{self.name} [{self.type}]"
        else:
            return f"{self.name}.{self.zone.name} [{self.type}]"

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:record", kwargs={"pk": self.id})

    def fqdn(self):
        return f"{self.name}.{self.zone.name}."

    def ptr_zone(self):
        address = ipaddress.ip_address(self.value)
        if address.version == 4:
            lengths = range(1, 4)
        else:
            lengths = range(16, 32)

        zone_names = [
            ".".join(address.reverse_pointer.split(".")[length:]) for length in lengths
        ]

        ptr_zones = Zone.objects.filter(Q(name__in=zone_names)).order_by(
            Length("name").desc()
        )
        if len(ptr_zones):
            return ptr_zones[0]

    def update_ptr_record(self):
        ptr_zone = self.ptr_zone()

        if ptr_zone is None or self.disable_ptr:
            if self.ptr_record is not None:
                with transaction.atomic():
                    self.ptr_record.delete()
                    self.ptr_record = None
            return

        ptr_name = ipaddress.ip_address(self.value).reverse_pointer.replace(
            f".{ptr_zone.name}", ""
        )
        ptr_value = self.fqdn()
        ptr_record = self.ptr_record

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
                    type=Record.PTR,
                    name=ptr_name,
                    ttl=self.ttl,
                    value=ptr_value,
                    managed=True,
                )

        self.ptr_record = ptr_record
        super().save()

    def save(self, *args, **kwargs):
        if self.type in (self.A, self.AAAA):
            self.update_ptr_record()

        super().save(*args, **kwargs)

        zone = self.zone
        if self.type != self.SOA and zone.soa_serial_auto:
            zone.update_serial()

    def delete(self, *args, **kwargs):
        if self.ptr_record:
            self.ptr_record.delete()

        super().delete(*args, **kwargs)

        zone = self.zone
        if zone.soa_serial_auto:
            zone.update_serial()
