from django import forms
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse_lazy

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    TagFilterField,
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect, APISelect
from utilities.forms.rendering import FieldSet
from utilities.forms import add_blank_choice
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import (
    View,
    Zone,
    NameServer,
    Registrar,
    Contact,
)
from netbox_dns.choices import ZoneStatusChoices
from netbox_dns.utilities import name_to_unicode
from netbox_dns.fields import RFC2317NetworkFormField
from netbox_dns.validators import validate_ipv4, validate_prefix, validate_rfc2317


__ALL__ = (
    "ZoneForm",
    "ZoneFilterForm",
    "ZoneImportForm",
    "ZoneBulkEditForm",
)


class ZoneForm(TenancyForm, NetBoxModelForm):
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    default_ttl = forms.IntegerField(
        required=False,
        label="Default TTL",
        help_text="Default TTL for new records in this zone",
        validators=[MinValueValidator(1)],
    )
    soa_ttl = forms.IntegerField(
        required=True,
        label="SOA TTL",
        help_text="TTL for the SOA record of the zone",
        validators=[MinValueValidator(1)],
    )
    soa_rname = forms.CharField(
        required=True,
        label="SOA RName",
        help_text="Mailbox of the zone's administrator",
    )
    soa_serial_auto = forms.BooleanField(
        required=False,
        label="Generate SOA Serial",
        help_text="Automatically generate the SOA Serial",
    )
    soa_serial = forms.IntegerField(
        required=False,
        label="SOA Serial",
        help_text="Serial number of the current zone data version",
        validators=[MinValueValidator(1)],
    )
    soa_refresh = forms.IntegerField(
        required=True,
        label="SOA Refresh",
        help_text="Refresh interval for secondary name servers",
        validators=[MinValueValidator(1)],
    )
    soa_retry = forms.IntegerField(
        required=True,
        label="SOA Retry",
        help_text="Retry interval for secondary name servers",
        validators=[MinValueValidator(1)],
    )
    soa_expire = forms.IntegerField(
        required=True,
        label="SOA Expire",
        help_text="Expire time after which the zone is considered unavailable",
        validators=[MinValueValidator(1)],
    )
    soa_minimum = forms.IntegerField(
        required=True,
        label="SOA Minimum TTL",
        help_text="Minimum TTL for negative results, e.g. NXRRSET",
        validators=[MinValueValidator(1)],
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        label="RFC2317 Prefix",
        help_text="IPv4 network prefix with a mask length of at least 25 bits",
        validators=[validate_ipv4, validate_prefix, validate_rfc2317],
        required=False,
    )
    rfc2317_parent_managed = forms.BooleanField(
        label="RFC2317 Parent Managed",
        help_text="IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS",
        required=False,
    )

    fieldsets = (
        FieldSet(
            "view",
            "name",
            "status",
            "nameservers",
            "default_ttl",
            "description",
            name="Zone",
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
            name="SOA",
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            name="RFC 2317",
        ),
        FieldSet(
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name="Domain Registration",
        ),
        FieldSet("tags", name="Tags"),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
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

        if self.initial.get("soa_serial_auto"):
            self.initial["soa_serial"] = None

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
            "nameservers",
            "default_ttl",
            "description",
            "tags",
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
        )
        help_texts = {
            "view": "View the zone belongs to",
            "soa_mname": "Primary name server for the zone",
        }


class ZoneFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Zone
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "view_id", "status", "name", "nameservers", "description", name="Attributes"
        ),
        FieldSet(
            "soa_mname_id",
            "soa_rname",
            "soa_serial_auto",
            name="SOA",
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            "rfc2317_parent_zone_id",
            name="RFC2317",
        ),
        FieldSet(
            "registrar_id",
            "registry_domain_id",
            "registrant_id",
            "admin_c_id",
            "tech_c_id",
            "billing_c_id",
            name="Registration",
        ),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    view_id = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        label="View",
    )
    status = forms.MultipleChoiceField(
        choices=ZoneStatusChoices,
        required=False,
    )
    name = forms.CharField(
        required=False,
    )
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    soa_mname_id = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        label="MName",
        required=False,
    )
    soa_rname = forms.CharField(
        required=False,
        label="RName",
    )
    soa_serial_auto = forms.NullBooleanField(
        required=False,
        label="Generate Serial",
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        label="Prefix",
    )
    rfc2317_parent_managed = forms.NullBooleanField(
        required=False,
        label="Parent Managed",
    )
    rfc2317_parent_zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="Parent Zone",
    )
    registrar_id = DynamicModelMultipleChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label="Registrar",
    )
    registry_domain_id = forms.CharField(
        required=False,
        label="Registry Domain ID",
    )
    registrant_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Registrant",
    )
    admin_c_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Admin-C",
    )
    tech_c_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Tech-C",
    )
    billing_c_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Billing-C",
    )
    tag = TagFilterField(Zone)


class ZoneImportForm(NetBoxModelImportForm):
    view = CSVModelChoiceField(
        queryset=View.objects.all(),
        required=False,
        to_field_name="name",
        help_text="View the zone belongs to",
        error_messages={
            "invalid_choice": "View not found.",
        },
    )
    status = CSVChoiceField(
        choices=ZoneStatusChoices,
        required=False,
        help_text="Zone status",
    )
    nameservers = CSVModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Name servers for the zone",
    )
    default_ttl = forms.IntegerField(
        required=False,
        help_text="Default TTL",
    )
    soa_ttl = forms.IntegerField(
        required=False,
        help_text="TTL for the SOA record of the zone",
    )
    soa_mname = CSVModelChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Primary name server for the zone",
        error_messages={
            "invalid_choice": "Nameserver not found.",
        },
    )
    soa_rname = forms.CharField(
        required=False,
        help_text="Mailbox of the zone's administrator",
    )
    soa_serial_auto = forms.NullBooleanField(
        required=False,
        help_text="Generate the SOA serial",
    )
    soa_serial = forms.IntegerField(
        required=False,
        help_text="Serial number of the current zone data version",
    )
    soa_refresh = forms.IntegerField(
        required=False,
        help_text="Refresh interval for secondary name servers",
    )
    soa_retry = forms.IntegerField(
        required=False,
        help_text="Retry interval for secondary name servers",
    )
    soa_expire = forms.IntegerField(
        required=False,
        help_text="Expire time after which the zone is considered unavailable",
    )
    soa_minimum = forms.IntegerField(
        required=False,
        help_text="Minimum TTL for negative results, e.g. NXRRSET",
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        help_text="RFC2317 IPv4 prefix with a length of at least 25 bits",
    )
    rfc2317_parent_managed = forms.BooleanField(
        required=False,
        label="RFC2317 Parent Managed",
        help_text="IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS",
    )
    registrar = CSVModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Registrar the domain is registered with",
        error_messages={
            "invalid_choice": "Registrar not found.",
        },
    )
    registry_domain_id = forms.CharField(
        required=False,
        help_text="Domain ID assigned by the registry",
    )
    registrant = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        to_field_name="contact_id",
        help_text="Owner of the domain",
        error_messages={
            "invalid_choice": "Registrant contact ID not found",
        },
    )
    admin_c = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        to_field_name="contact_id",
        help_text="Administrative contact for the domain",
        error_messages={
            "invalid_choice": "Administrative contact ID not found",
        },
    )
    tech_c = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        to_field_name="contact_id",
        help_text="Technical contact for the domain",
        error_messages={
            "invalid_choice": "Technical contact ID not found",
        },
    )
    billing_c = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        to_field_name="contact_id",
        help_text="Billing contact for the domain",
        error_messages={
            "invalid_choice": "Billing contact ID not found",
        },
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )

    class Meta:
        model = Zone

        fields = (
            "view",
            "name",
            "status",
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
        label="View",
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:view-list")}
        ),
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(ZoneStatusChoices),
        required=False,
    )
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    default_ttl = forms.IntegerField(
        required=False,
        label="Default TTL",
        validators=[MinValueValidator(1)],
    )
    description = forms.CharField(max_length=200, required=False)
    soa_ttl = forms.IntegerField(
        required=False,
        label="SOA TTL",
        validators=[MinValueValidator(1)],
    )
    soa_mname = DynamicModelChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label="SOA Primary Nameserver",
        widget=APISelect(
            attrs={
                "data-url": reverse_lazy("plugins-api:netbox_dns-api:nameserver-list")
            }
        ),
    )
    soa_rname = forms.CharField(
        required=False,
        label="SOA RName",
    )
    soa_serial_auto = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label="Generate SOA Serial",
    )
    soa_serial = forms.IntegerField(
        required=False,
        label="SOA Serial",
        validators=[MinValueValidator(1), MaxValueValidator(4294967295)],
    )
    soa_refresh = forms.IntegerField(
        required=False,
        label="SOA Refresh",
        validators=[MinValueValidator(1)],
    )
    soa_retry = forms.IntegerField(
        required=False,
        label="SOA Retry",
        validators=[MinValueValidator(1)],
    )
    soa_expire = forms.IntegerField(
        required=False,
        label="SOA Expire",
        validators=[MinValueValidator(1)],
    )
    soa_minimum = forms.IntegerField(
        required=False,
        label="SOA Minimum TTL",
        validators=[MinValueValidator(1)],
    )
    rfc2317_prefix = RFC2317NetworkFormField(
        required=False,
        label="RFC2317 Prefix",
        help_text="IPv4 network prefix with a mask length of at least 25 bits",
        validators=[validate_ipv4, validate_prefix, validate_rfc2317],
    )
    rfc2317_parent_managed = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label="RFC2317 Parent Managed",
        help_text="IPv4 reverse zone for deletgating the RFC2317 PTR records is managed in NetBox DNS",
    )
    registrar = DynamicModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        widget=APISelect(
            attrs={
                "data-url": reverse_lazy("plugins-api:netbox_dns-api:registrar-list")
            }
        ),
    )
    registry_domain_id = forms.CharField(
        required=False,
        label="Registry Domain ID",
    )
    registrant = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:contact-list")}
        ),
    )
    admin_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Administrative Contact",
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:contact-list")}
        ),
    )
    tech_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Technical Contact",
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:contact-list")}
        ),
    )
    billing_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Billing Contact",
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:contact-list")}
        ),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    model = Zone

    fieldsets = (
        FieldSet(
            "view",
            "status",
            "nameservers",
            "default_ttl",
            "description",
            name="Attributes",
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
            name="SOA",
        ),
        FieldSet(
            "rfc2317_prefix",
            "rfc2317_parent_managed",
            name="RFC 2317",
        ),
        FieldSet(
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name="Domain Registration",
        ),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
    )

    nullable_fields = (
        "description",
        "rfc2317_prefix",
        "registrar",
        "registry_domain_id",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    )
