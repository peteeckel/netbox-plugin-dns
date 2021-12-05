from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    validate_ipv6_address,
    validate_ipv4_address,
)
from django.forms import (
    CharField,
    IntegerField,
    BooleanField,
    NullBooleanField,
)
from django.urls import reverse_lazy

from extras.forms import (
    CustomFieldModelForm,
    CustomFieldModelCSVForm,
    AddRemoveTagsForm,
    CustomFieldModelBulkEditForm,
    CustomFieldModelFilterForm,
)
from extras.models.tags import Tag
from utilities.forms import (
    BootstrapMixin,
    BulkEditNullBooleanSelect,
    DynamicModelMultipleChoiceField,
    TagFilterField,
    StaticSelect,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    APISelect,
    StaticSelectMultiple,
    add_blank_choice,
)
from .fields import CustomDynamicModelMultipleChoiceField
from .models import NameServer, Record, Zone


class ZoneForm(BootstrapMixin, CustomFieldModelForm):
    """Form for creating a new Zone object."""

    def __init__(self, *args, **kwargs):
        """Override the __init__ method in order to provide the initial value for the default fields"""
        super().__init__(*args, **kwargs)

        defaults = settings.PLUGINS_CONFIG.get("netbox_dns")

        def _initialize(initial, setting):
            if initial.get(setting, None) in (None, ""):
                initial[setting] = defaults.get(f"zone_{setting}", None)

        for setting in (
            "default_ttl",
            "soa_ttl",
            "soa_mname",
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

    def clean_default_ttl(self):
        return (
            self.cleaned_data["default_ttl"]
            if self.cleaned_data["default_ttl"]
            else self.initial["default_ttl"]
        )

    nameservers = CustomDynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    default_ttl = IntegerField(
        required=False,
        label="Default TTL",
        help_text="Default TTL for new records in this zone",
        validators=[MinValueValidator(1)],
    )
    soa_ttl = IntegerField(
        required=True,
        label="SOA TTL",
        help_text="TTL for the SOA record of the zone",
        validators=[MinValueValidator(1)],
    )
    soa_rname = CharField(
        required=True,
        label="SOA Responsible",
        help_text="Mailbox of the zone's administrator",
    )
    soa_serial_auto = BooleanField(
        required=False,
        label="Generate SOA Serial",
        help_text="Automatically generate the SOA Serial",
    )
    soa_serial = IntegerField(
        required=False,
        label="SOA Serial",
        help_text="Serial number of the current zone data version",
        validators=[MinValueValidator(1)],
    )
    soa_refresh = IntegerField(
        required=True,
        label="SOA Refresh",
        help_text="Refresh interval for secondary name servers",
        validators=[MinValueValidator(1)],
    )
    soa_retry = IntegerField(
        required=True,
        label="SOA Retry",
        help_text="Retry interval for secondary name servers",
        validators=[MinValueValidator(1)],
    )
    soa_expire = IntegerField(
        required=True,
        label="SOA Expire",
        help_text="Expire time after which the zone is considered unavailable",
        validators=[MinValueValidator(1)],
    )
    soa_minimum = IntegerField(
        required=True,
        label="SOA Minimum TTL",
        help_text="Minimum TTL for negative results, e.g. NXRRSET",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        model = Zone
        fields = (
            "name",
            "status",
            "nameservers",
            "default_ttl",
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
        )
        widgets = {
            "status": StaticSelect(),
            "soa_mname": StaticSelect(),
        }
        help_texts = {
            "soa_mname": "Primary name server for the zone",
        }


class ZoneFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    """Form for filtering Zone instances."""

    model = Zone

    q = CharField(required=False, label="Search")
    status = forms.ChoiceField(
        choices=add_blank_choice(Zone.CHOICES),
        required=False,
        widget=StaticSelect(),
    )
    name = CharField(
        required=False,
        label="Name",
    )
    nameservers = CustomDynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    tag = TagFilterField(Zone)


class ZoneCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=Zone.CHOICES,
        help_text="Zone status",
    )

    default_ttl = IntegerField(
        required=False,
        help_text="Default TTL",
    )
    soa_ttl = IntegerField(
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
    soa_rname = CharField(
        required=False,
        help_text="Mailbox of the zone's administrator",
    )
    soa_serial_auto = BooleanField(
        required=False,
        help_text="Generate the SOA serial",
    )
    soa_serial = IntegerField(
        required=False,
        help_text="Serial number of the current zone data version",
    )
    soa_refresh = IntegerField(
        required=False,
        help_text="Refresh interval for secondary name servers",
    )
    soa_retry = IntegerField(
        required=False,
        help_text="Retry interval for secondary name servers",
    )
    soa_expire = IntegerField(
        required=False,
        help_text="Expire time after which the zone is considered unavailable",
    )
    soa_minimum = IntegerField(
        required=False,
        help_text="Minimum TTL for negative results, e.g. NXRRSET",
    )

    def _get_default_value(self, field):
        _default_values = settings.PLUGINS_CONFIG.get("netbox_dns", dict())
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
        return self._clean_field_with_defaults("soa_mname")

    def clean_soa_rname(self):
        return self._clean_field_with_defaults("soa_rname")

    def clean_soa_serial_auto(self):
        try:
            return self._clean_field_with_defaults("soa_serial_auto")
        except ValidationError:
            if self.cleaned_data["soa_serial"] or self._get_default_value("soa_serial"):
                return None
            else:
                raise

    def clean_soa_serial(self):
        try:
            return self._clean_field_with_defaults("soa_serial")
        except ValidationError:
            if self.cleaned_data["soa_serial_auto"] or self._get_default_value(
                "soa_serial_auto"
            ):
                return None
            else:
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
            "name",
            "status",
            "default_ttl",
            "soa_ttl",
            "soa_mname",
            "soa_rname",
            "soa_serial_auto",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
        )


class ZoneBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(Zone.CHOICES),
        required=False,
        widget=StaticSelect(),
    )
    nameservers = CustomDynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    default_ttl = IntegerField(
        required=False,
        label="Default TTL",
        validators=[MinValueValidator(1)],
    )
    soa_ttl = IntegerField(
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
    soa_rname = CharField(
        required=False,
        label="SOA Responsible",
    )
    soa_serial_auto = NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label="Generate SOA Serial",
    )
    soa_serial = IntegerField(
        required=False,
        label="SOA Serial",
        validators=[MinValueValidator(1), MaxValueValidator(4294967295)],
    )
    soa_refresh = IntegerField(
        required=False,
        label="SOA Refresh",
        validators=[MinValueValidator(1)],
    )
    soa_retry = IntegerField(
        required=False,
        label="SOA Retry",
        validators=[MinValueValidator(1)],
    )
    soa_expire = IntegerField(
        required=False,
        label="SOA Expire",
        validators=[MinValueValidator(1)],
    )
    soa_minimum = IntegerField(
        required=False,
        label="SOA Minimum TTL",
        validators=[MinValueValidator(1)],
    )

    def clean(self):
        """
        If soa_serial_auto is True, set soa_serial to None.
        """
        cleaned_data = super().clean()
        if cleaned_data.get("soa_serial_auto"):
            cleaned_data["soa_serial"] = None

    class Meta:
        nullable_fields = []

        model = Zone
        fields = (
            "name",
            "status",
            "nameservers",
            "default_ttl",
            "tags",
            "soa_ttl",
            "soa_rname",
            "soa_serial_auto",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
        )
        widgets = {
            "status": StaticSelect(),
        }


class NameServerForm(BootstrapMixin, forms.ModelForm):
    """Form for creating a new NameServer object."""

    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    class Meta:
        model = NameServer
        fields = ("name", "tags")


class NameServerFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    """Form for filtering NameServer instances."""

    model = NameServer

    q = CharField(
        required=False,
        label="Search",
    )
    name = CharField(
        required=False,
        label="Name",
    )
    tag = TagFilterField(NameServer)


class NameServerCSVForm(CustomFieldModelCSVForm):
    class Meta:
        model = NameServer
        fields = ("name",)


class RecordForm(BootstrapMixin, forms.ModelForm):
    """Form for creating a new Record object."""

    def clean(self):
        """
        For A and AAA records, verify that a valid IPv4 or IPv6 was passed as
        value and raise a ValidationError exception otherwise.
        """
        cleaned_data = super().clean()

        type = cleaned_data.get("type")
        if type not in (Record.A, Record.AAAA):
            return

        value = cleaned_data.get("value")
        try:
            ip_version = "4" if type == Record.A else "6"
            if type == Record.A:
                validate_ipv4_address(value)
            else:
                validate_ipv6_address(value)

        except ValidationError:
            raise forms.ValidationError(
                {
                    "value": f"A valid IPv{ip_version} address is required for record type {type}."
                }
            )

        if cleaned_data.get("disable_ptr"):
            return

        pk = cleaned_data.get("pk")
        conflicts = Record.objects.filter(value=value, type=type, disable_ptr=False)
        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)
        if len(conflicts):
            raise forms.ValidationError(
                {
                    "value": f"There is already an {type} record with value {value} and PTR enabled."
                }
            )

    def clean_ttl(self):
        ttl = self.cleaned_data["ttl"]
        if ttl is not None:
            if ttl <= 0:
                raise ValidationError("TTL must be greater than zero")
            return ttl
        else:
            return self.cleaned_data["zone"].default_ttl

    disable_ptr = BooleanField(
        label="Disable PTR",
        required=False,
    )

    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    ttl = IntegerField(
        required=False,
        label="TTL",
    )

    class Meta:
        model = Record
        fields = ("zone", "type", "disable_ptr", "name", "value", "ttl", "tags")

        widgets = {
            "zone": StaticSelect(),
            "type": StaticSelect(),
        }


class RecordFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    """Form for filtering Record instances."""

    model = Record

    q = CharField(
        required=False,
        label="Search",
    )
    type = forms.MultipleChoiceField(
        choices=add_blank_choice(Record.CHOICES),
        required=False,
        widget=StaticSelectMultiple(),
    )
    name = CharField(
        required=False,
        label="Name",
    )
    value = CharField(
        required=False,
        label="Value",
    )
    zone_id = CustomDynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        label="Zone",
    )
    tag = TagFilterField(Record)


class RecordCSVForm(CustomFieldModelCSVForm):
    zone = CSVModelChoiceField(
        queryset=Zone.objects.all(),
        to_field_name="name",
        required=True,
        help_text="Assigned zone",
    )
    type = CSVChoiceField(
        choices=Record.CHOICES,
        required=True,
        help_text="Record Type",
    )
    ttl = IntegerField(
        required=False,
        help_text="TTL",
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label="Disable PTR",
        help_text="Disable generation of a PTR record",
    )

    def clean(self):
        """
        For A and AAA records, verify that a valid IPv4 or IPv6 was passed as
        value and raise a ValidationError exception otherwise.
        """
        cleaned_data = super().clean()

        type = cleaned_data.get("type")
        if type not in (Record.A, Record.AAAA):
            return

        value = cleaned_data.get("value")
        try:
            ip_version = "4" if type == Record.A else "6"
            if type == Record.A:
                validate_ipv4_address(value)
            else:
                validate_ipv6_address(value)

        except ValidationError:
            raise forms.ValidationError(
                {
                    "value": f"A valid IPv{ip_version} address is required for record type {type}."
                }
            )

        if cleaned_data.get("disable_ptr"):
            return

        conflicts = Record.objects.filter(value=value, type=type, disable_ptr=False)
        if len(conflicts):
            raise forms.ValidationError(
                {
                    "value": f"There is already an {type} record with value {value} and PTR enabled."
                }
            )

    def clean_ttl(self):
        ttl = self.cleaned_data["ttl"]
        if ttl is not None:
            if ttl <= 0:
                raise ValidationError("TTL must be greater than zero")
            return ttl
        elif "zone" in self.cleaned_data:
            return self.cleaned_data["zone"].default_ttl

    class Meta:
        model = Record
        fields = ("zone", "type", "name", "value", "ttl", "disable_ptr")


class RecordBulkEditForm(
    BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(
        queryset=Record.objects.all(), widget=forms.MultipleHiddenInput()
    )
    zone = DynamicModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_dns-api:zone-list")}
        ),
    )
    disable_ptr = NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label="Disable PTR"
    )
    ttl = IntegerField(
        required=False,
        label="TTL",
    )

    def clean(self):
        """
        For A and AAA records, verify that a valid IPv4 or IPv6 was passed as
        value and raise a ValidationError exception otherwise.
        """
        cleaned_data = super().clean()

        disable_ptr = cleaned_data.get("disable_ptr")
        if disable_ptr is None or disable_ptr:
            return

        for record in cleaned_data.get("pk"):
            conflicts = (
                Record.objects.filter(Record.unique_ptr_qs)
                .filter(value=record.value)
                .exclude(pk=record.pk)
            )
            if len(conflicts):
                raise forms.ValidationError(
                    {
                        "disable_ptr": f"Multiple {record.type} records with value {record.value} and PTR enabled."
                    }
                )

    def clean_ttl(self):
        ttl = self.cleaned_data["ttl"]
        if ttl is not None:
            if ttl <= 0:
                raise ValidationError("TTL must be greater than zero")
            return ttl

    class Meta:
        model = Record
        fields = ("zone", "ttl", "disable_ptr", "tags")
        nullable_fields = []

        widgets = {
            "zone": StaticSelect(),
        }
