from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
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
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect, APISelect
from utilities.forms import add_blank_choice
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import View, Zone, ZoneStatusChoices, NameServer
from netbox_dns.utilities import name_to_unicode


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
        label="SOA Responsible",
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
    fieldsets = (
        (
            "Zone",
            (
                "view",
                "name",
                "status",
                "nameservers",
                "default_ttl",
                "description",
            ),
        ),
        (
            "SOA",
            (
                "soa_ttl",
                "soa_mname",
                "soa_rname",
                "soa_refresh",
                "soa_retry",
                "soa_expire",
                "soa_minimum",
                "soa_serial_auto",
                "soa_serial",
            ),
        ),
        ("Tags", ("tags",)),
        ("Tenancy", ("tenant_group", "tenant")),
    )

    def __init__(self, *args, **kwargs):
        """Override the __init__ method in order to provide the initial value for the default fields"""
        super().__init__(*args, **kwargs)

        initial_name = self.initial.get("name")
        if initial_name:
            self.initial["name"] = name_to_unicode(initial_name)

        defaults = settings.PLUGINS_CONFIG.get("netbox_dns")

        def _initialize(initial, setting):
            if initial.get(setting, None) in (None, ""):
                initial[setting] = defaults.get(f"zone_{setting}", None)

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
            _initialize(self.initial, setting)

        if self.initial.get("soa_ttl", None) is None:
            self.initial["soa_ttl"] = self.initial.get("default_ttl", None)

        if self.initial.get("soa_serial_auto"):
            self.initial["soa_serial"] = None

        if self.initial.get("soa_mname", None) in (None, ""):
            default_soa_mname = defaults.get("zone_soa_mname", None)
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
            "tenant",
        )
        help_texts = {
            "view": "View the zone belongs to",
            "soa_mname": "Primary name server for the zone",
        }


class ZoneFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Zone
    fieldsets = (
        (None, ("q", "filter_id", "tag")),
        ("Attributes", ("view_id", "status", "name", "nameservers")),
        ("Tenant", ("tenant_group_id", "tenant_id")),
    )

    view_id = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        label="View",
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(ZoneStatusChoices),
        required=False,
    )
    name = forms.CharField(
        required=False,
        label="Name",
    )
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
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
    soa_serial_auto = forms.BooleanField(
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
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )

    def _get_default_value(self, field):
        _default_values = settings.PLUGINS_CONFIG.get("netbox_dns", {})
        if _default_values.get("zone_soa_ttl", None) is None:
            _default_values["zone_soa_ttl"] = _default_values.get(
                "zone_default_ttl", None
            )

        return _default_values.get(f"zone_{field}", None)

    def _clean_field_with_defaults(self, field):
        if self.cleaned_data[field]:
            value = self.cleaned_data[field]
        else:
            value = self._get_default_value(field)

        if value is None:
            raise ValidationError(f"{field} not set and no default value available")

        return value

    def clean_default_ttl(self):
        return self._clean_field_with_defaults("default_ttl")

    def clean_soa_ttl(self):
        return self._clean_field_with_defaults("soa_ttl")

    def clean_soa_mname(self):
        soa_mname = self._clean_field_with_defaults("soa_mname")
        if type(soa_mname) == str:
            try:
                soa_mname = NameServer.objects.get(name=soa_mname)
            except NameServer.DoesNotExist:
                raise ValidationError(f"Default name server {soa_mname} does not exist")

        return soa_mname

    def clean_soa_rname(self):
        return self._clean_field_with_defaults("soa_rname")

    def clean_soa_serial_auto(self):
        try:
            return self._clean_field_with_defaults("soa_serial_auto")
        except ValidationError:
            if self.cleaned_data["soa_serial"] or self._get_default_value("soa_serial"):
                return None

            raise

    def clean_soa_serial(self):
        try:
            return self._clean_field_with_defaults("soa_serial")
        except ValidationError:
            if self.cleaned_data["soa_serial_auto"] or self._get_default_value(
                "soa_serial_auto"
            ):
                return None

            raise

    def clean_soa_refresh(self):
        return self._clean_field_with_defaults("soa_refresh")

    def clean_soa_retry(self):
        return self._clean_field_with_defaults("soa_retry")

    def clean_soa_expire(self):
        return self._clean_field_with_defaults("soa_expire")

    def clean_soa_minimum(self):
        return self._clean_field_with_defaults("soa_minimum")

    class Meta:
        model = Zone

        fields = (
            "view",
            "name",
            "status",
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
            "tenant",
        )


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
        label="SOA Responsible",
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
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    model = Zone

    fieldsets = (
        (
            None,
            (
                "view",
                "status",
                "nameservers",
                "default_ttl",
                "description",
                "tenant",
            ),
        ),
        (
            "SOA",
            (
                "soa_ttl",
                "soa_mname",
                "soa_rname",
                "soa_serial_auto",
                "soa_serial",
                "soa_refresh",
                "soa_retry",
                "soa_expire",
                "soa_minimum",
            ),
        ),
    )
    nullable_fields = ("view", "description")

    def clean(self):
        """
        If soa_serial_auto is True, set soa_serial to None.
        """
        cleaned_data = super().clean()
        if cleaned_data.get("soa_serial_auto"):
            cleaned_data["soa_serial"] = None
