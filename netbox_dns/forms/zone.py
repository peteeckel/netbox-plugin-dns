from django import forms
from django.db import transaction
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as _p

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from netbox.context import events_queue
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    TagFilterField,
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms.rendering import FieldSet
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import (
    View,
    Zone,
    NameServer,
    Registrar,
    RegistrationContact,
    ZoneTemplate,
)
from netbox_dns.choices import ZoneStatusChoices
from netbox_dns.utilities import name_to_unicode
from netbox_dns.fields import RFC2317NetworkFormField
from netbox_dns.validators import validate_ipv4, validate_prefix, validate_rfc2317


__all__ = (
    "ZoneForm",
    "ZoneFilterForm",
    "ZoneImportForm",
    "ZoneBulkEditForm",
)


class RollbackTransaction(Exception):
    pass


class ZoneTemplateUpdateMixin:
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        if (template := self.cleaned_data.get("template")) is None:
            return

        if not self.cleaned_data.get("nameservers") and template.nameservers.all():
            self.cleaned_data["nameservers"] = template.nameservers.all()

        if not self.cleaned_data.get("tags") and template.tags.all():
            self.cleaned_data["tags"] = template.tags.all()

        for field in template.template_fields:
            if (
                self.cleaned_data.get(field) is None
                and getattr(template, field) is not None
            ):
                self.cleaned_data[field] = getattr(template, field)

        template_error = None
        saved_events_queue = events_queue.get()

        try:
            with transaction.atomic():
                if self.instance.id is not None:
                    zone = super().save(*args, **kwargs)
                else:
                    zone_data = self.cleaned_data.copy()

                    custom_fields = {}
                    for key, value in zone_data.copy().items():
                        if key.startswith("cf_"):
                            custom_fields[key[3:]] = value
                            zone_data.pop(key)
                    if custom_fields:
                        zone_data["custom_field_data"] = custom_fields

                    zone_data.pop("template", None)
                    zone_data.pop("tenant_group", None)
                    zone_data.pop("_init_time", None)

                    nameservers = zone_data.pop("nameservers")
                    tags = zone_data.pop("tags")

                    zone = Zone.objects.create(**zone_data)

                    zone.nameservers.set(nameservers)
                    zone.tags.set(tags)

                template.create_records(zone)
                raise RollbackTransaction

        except ValidationError as exc:
            self.add_error("template", exc.messages)
        except RollbackTransaction:
            pass

        events_queue.set(saved_events_queue)
        if template_error is not None:
            raise ValidationError({"template": template_error})

        return self.cleaned_data

    def save(self, *args, **kwargs):
        zone = super().save(*args, **kwargs)

        if (template := self.cleaned_data.get("template")) is not None:
            template.create_records(zone)

        return zone


class ZoneForm(ZoneTemplateUpdateMixin, TenancyForm, NetBoxModelForm):
    name = forms.CharField(
        required=True,
        label=_("Name"),
    )
    template = DynamicModelChoiceField(
        queryset=ZoneTemplate.objects.all(),
        required=False,
        label=_("Template"),
    )
    status = forms.ChoiceField(
        choices=ZoneStatusChoices,
        required=False,
        label=_("Status"),
    )
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("Nameservers"),
    )
    default_ttl = forms.IntegerField(
        required=False,
        help_text=_("Default TTL for new records in this zone"),
        validators=[MinValueValidator(1)],
        label=_("Default TTL"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    soa_ttl = forms.IntegerField(
        required=True,
        help_text=_("TTL for the SOA record of the zone"),
        validators=[MinValueValidator(1)],
        label=_("SOA TTL"),
    )
    soa_rname = forms.CharField(
        required=True,
        help_text=_("Mailbox of the zone's administrator"),
        label=_("SOA RName"),
    )
    soa_refresh = forms.IntegerField(
        required=True,
        help_text=_("Refresh interval for secondary nameservers"),
        validators=[MinValueValidator(1)],
        label=_("SOA Refresh"),
    )
    soa_retry = forms.IntegerField(
        required=True,
        help_text=_("Retry interval for secondary nameservers"),
        validators=[MinValueValidator(1)],
        label=_("SOA Retry"),
    )
    soa_expire = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1)],
        help_text=_("Expire time after which the zone is considered unavailable"),
        label=_("SOA Expire"),
    )
    soa_minimum = forms.IntegerField(
        required=True,
        help_text=_("Minimum TTL for negative results, e.g. NXRRSET, NXDOMAIN"),
        validators=[MinValueValidator(1)],
        label=_("SOA Minimum TTL"),
    )
    soa_serial_auto = forms.BooleanField(
        required=False,
        help_text=_("Automatically generate the SOA serial number"),
        label=_("Generate SOA Serial"),
    )
    soa_serial = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA Serial"),
    )

    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        validators=[validate_ipv4, validate_prefix, validate_rfc2317],
        help_text=_("RFC2317 IPv4 prefix with a length of at least 25 bits"),
        label=_("RFC2317 Prefix"),
    )
    rfc2317_parent_managed = forms.BooleanField(
        required=False,
        help_text=_(
            "IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS"
        ),
        label=_("RFC2317 Parent Managed"),
    )

    fieldsets = (
        FieldSet(
            "view",
            "name",
            "template",
            "status",
            "nameservers",
            "default_ttl",
            "description",
            name=_("Zone"),
        ),
        FieldSet(
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "soa_serial_auto",
            "soa_serial",
            name=_("SOA"),
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            name=_("RFC2317"),
        ),
        FieldSet(
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name=_("Domain Registration"),
        ),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

        if self.initial.get("view") is None:
            self.initial["view"] = View.get_default_view()

        defaults = settings.PLUGINS_CONFIG.get("netbox_dns")
        for setting in (
            "default_ttl",
            "soa_ttl",
            "soa_rname",
            "soa_serial_auto",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
        ):
            if self.initial.get(setting) in (None, ""):
                self.initial[setting] = defaults.get(f"zone_{setting}")

        if self.initial.get("soa_ttl") is None:
            self.initial["soa_ttl"] = self.initial.get("default_ttl")

        if self.initial.get("soa_mname") is None:
            default_soa_mname = defaults.get("zone_soa_mname")
            if default_soa_mname is not None:
                try:
                    self.initial["soa_mname"] = NameServer.objects.get(
                        name=default_soa_mname
                    )
                except NameServer.DoesNotExist:
                    pass

        if not self.initial.get("nameservers", []):
            default_nameservers = defaults.get("zone_nameservers", [])
            if default_nameservers:
                self.initial["nameservers"] = NameServer.objects.filter(
                    name__in=default_nameservers
                )

    def clean_default_ttl(self):
        return (
            self.cleaned_data["default_ttl"]
            if self.cleaned_data["default_ttl"]
            else self.initial["default_ttl"]
        )

    class Meta:
        model = Zone

        fields = (
            "name",
            "view",
            "status",
            "template",
            "nameservers",
            "default_ttl",
            "description",
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial_auto",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant_group",
            "tenant",
            "tags",
        )
        help_texts = {
            "soa_mname": _("Primary nameserver for the zone"),
        }


class ZoneFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Zone
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "view_id",
            "status",
            "name",
            "nameserver_id",
            "active",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "soa_mname_id",
            "soa_rname",
            "soa_serial_auto",
            name=_("SOA"),
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            "rfc2317_parent_zone_id",
            name=_("RFC2317"),
        ),
        FieldSet(
            "registrar_id",
            "registry_domain_id",
            "registrant_id",
            "admin_c_id",
            "tech_c_id",
            "billing_c_id",
            name=_("Registration"),
        ),
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
    )

    view_id = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        label=_p("DNS", "View"),
    )
    status = forms.MultipleChoiceField(
        choices=ZoneStatusChoices,
        required=False,
        label=_("Status"),
    )
    name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    nameserver_id = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("Nameservers"),
    )
    active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Active"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    soa_mname_id = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("MName"),
    )
    soa_rname = forms.CharField(
        required=False,
        label=_("RName"),
    )
    soa_serial_auto = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Generate SOA Serial"),
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        label=_("Prefix"),
    )
    rfc2317_parent_managed = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Parent Managed"),
    )
    rfc2317_parent_zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label=_("Parent Zone"),
    )
    registrar_id = DynamicModelMultipleChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label=_("Registrar"),
    )
    registry_domain_id = forms.CharField(
        required=False,
        label=_("Registry Domain ID"),
    )
    registrant_id = DynamicModelMultipleChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Registrant"),
    )
    admin_c_id = DynamicModelMultipleChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Administrative Contact"),
    )
    tech_c_id = DynamicModelMultipleChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Technical Contact"),
    )
    billing_c_id = DynamicModelMultipleChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Billing Contact"),
    )
    tag = TagFilterField(Zone)


class ZoneImportForm(ZoneTemplateUpdateMixin, NetBoxModelImportForm):
    view = CSVModelChoiceField(
        queryset=View.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": _("View not found."),
        },
        label=_("View"),
    )
    status = CSVChoiceField(
        choices=ZoneStatusChoices,
        required=False,
        label=_("Status"),
    )
    nameservers = CSVModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Nameservers"),
    )
    default_ttl = forms.IntegerField(
        required=False,
        label=_("Default TTL"),
    )
    soa_ttl = forms.IntegerField(
        required=False,
        help_text=_("TTL for the SOA record of the zone"),
        label=_("SOA TTL"),
    )
    soa_mname = CSVModelChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": _("Nameserver not found."),
        },
        help_text=_("Primary nameserver for the zone"),
        label=_("SOA MName"),
    )
    soa_rname = forms.CharField(
        required=False,
        help_text=_("Mailbox of the zone's administrator"),
        label=_("SOA RName"),
    )
    soa_serial_auto = forms.BooleanField(
        required=False,
        label=_("Generate SOA Serial"),
    )
    soa_serial = forms.IntegerField(
        required=False,
        label=_("SOA Serial"),
    )
    soa_refresh = forms.IntegerField(
        required=False,
        help_text=_("Refresh interval for secondary nameservers"),
        label=_("SOA Refresh"),
    )
    soa_retry = forms.IntegerField(
        required=False,
        help_text=_("Retry interval for secondary nameservers"),
        label=_("SOA Retry"),
    )
    soa_expire = forms.IntegerField(
        required=False,
        help_text=_("Expire time after which the zone is considered unavailable"),
        label=_("SOA Expire"),
    )
    soa_minimum = forms.IntegerField(
        required=False,
        help_text=_("Minimum TTL for negative results, e.g. NXRRSET, NXDOMAIN"),
        label=_("SOA Minimum TTL"),
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        help_text=_("RFC2317 IPv4 prefix with a length of at least 25 bits"),
        label=_("RFC2317 Prefix"),
    )
    rfc2317_parent_managed = forms.BooleanField(
        required=False,
        help_text=_(
            "IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS"
        ),
        label=_("RFC2317 Parent Managed"),
    )
    registrar = CSVModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": _("Registrar not found."),
        },
        label=_("Registrar"),
    )
    registry_domain_id = forms.CharField(
        required=False,
        label=_("Registry Domain ID"),
    )
    registrant = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Registrant contact ID not found"),
        },
        label=_("Registrant"),
    )
    admin_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Administrative contact ID not found"),
        },
        label=_("Administrative Contact"),
    )
    tech_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Technical contact ID not found"),
        },
        label=_("Technical Contact"),
    )
    billing_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Billing contact ID not found"),
        },
        label=_("Billing Contact"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Tenant"),
    )
    template = CSVModelChoiceField(
        queryset=ZoneTemplate.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Template"),
    )

    class Meta:
        model = Zone

        fields = (
            "view",
            "name",
            "status",
            "template",
            "nameservers",
            "default_ttl",
            "description",
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial_auto",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant",
            "tags",
        )

    def clean_view(self):
        view = self.cleaned_data.get("view")
        if view is None:
            return View.get_default_view()

        return view

    def clean_nameservers(self):
        nameservers = self.cleaned_data.get("nameservers")
        zone_defaults = settings.PLUGINS_CONFIG.get("netbox_dns")

        if (
            self.data.get("nameservers") is None
            and zone_defaults.get("zone_nameservers") is not None
        ):
            nameservers = NameServer.objects.filter(
                name__in=zone_defaults.get("zone_nameservers")
            )

        return nameservers


class ZoneBulkEditForm(NetBoxModelBulkEditForm):
    view = DynamicModelChoiceField(
        queryset=View.objects.all(),
        required=False,
        label=_p("DNS", "View"),
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(ZoneStatusChoices),
        required=False,
        label=_("Status"),
    )
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("Nameservers"),
    )
    default_ttl = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("Default TTL"),
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        label=_("Description"),
    )
    soa_ttl = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA TTL"),
    )
    soa_mname = DynamicModelChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("SOA MName"),
    )
    soa_rname = forms.CharField(
        required=False,
        label=_("SOA RName"),
    )
    soa_serial_auto = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Generate SOA Serial"),
    )
    soa_serial = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1), MaxValueValidator(4294967295)],
        label=_("SOA Serial"),
    )
    soa_refresh = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA Refresh"),
    )
    soa_retry = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA Retry"),
    )
    soa_expire = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA Expire"),
    )
    soa_minimum = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(1)],
        label=_("SOA Minimum TTL"),
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        validators=[validate_ipv4, validate_prefix, validate_rfc2317],
        help_text=_("RFC2317 IPv4 prefix with a length of at least 25 bits"),
        label=_("RFC2317 Prefix"),
    )
    rfc2317_parent_managed = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        help_text=_(
            "IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS"
        ),
        label=_("RFC2317 Parent Managed"),
    )
    registrar = DynamicModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label=_("Registrar"),
    )
    registry_domain_id = forms.CharField(
        required=False,
        label=_("Registry Domain ID"),
    )
    registrant = DynamicModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Registrant"),
    )
    admin_c = DynamicModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Administrative Contact"),
    )
    tech_c = DynamicModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Technical Contact"),
    )
    billing_c = DynamicModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        label=_("Billing Contact"),
    )
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )

    model = Zone

    fieldsets = (
        FieldSet(
            "view",
            "status",
            "nameservers",
            "default_ttl",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "soa_serial_auto",
            "soa_serial",
            name=_("SOA"),
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            name=_("RFC2317"),
        ),
        FieldSet(
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name=_("Domain Registration"),
        ),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
    )

    nullable_fields = (
        "description",
        "nameservers",
        "rfc2317_prefix",
        "registrar",
        "registry_domain_id",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
        "tenant",
    )
