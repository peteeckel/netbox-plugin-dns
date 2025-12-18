from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    PrimaryModelBulkEditForm,
    PrimaryModelFilterSetForm,
    PrimaryModelImportForm,
    PrimaryModelForm,
)
from utilities.forms.fields import (
    TagFilterField,
    CSVModelChoiceField,
    CSVChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate, Zone, ZoneTemplate
from netbox_dns.choices import DNSSECPolicyDigestChoices, DNSSECPolicyStatusChoices
from netbox_dns.fields import TimePeriodField


__all__ = (
    "DNSSECPolicyForm",
    "DNSSECPolicyFilterForm",
    "DNSSECPolicyImportForm",
    "DNSSECPolicyBulkEditForm",
)


class DNSSECPolicyForm(TenancyForm, PrimaryModelForm):
    class Meta:
        model = DNSSECPolicy

        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "status",
            "inline_signing",
            "key_templates",
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            "tenant_group",
            "tenant",
            "tags",
        )

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "status",
            "key_templates",
            "inline_signing",
            name=_("Attributes"),
        ),
        FieldSet(
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            name=_("Timing"),
        ),
        FieldSet(
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            name=_("Parent Delegation"),
        ),
        FieldSet(
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            name=_("Proof of Non-Existence"),
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
        FieldSet(
            "tags",
            name=_("Tags"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.initial.get("use_nsec3"):
            self.initial["nsec3_iterations"] = None
            self.initial["nsec3_opt_out"] = None
            self.initial["nsec3_salt_size"] = None

    key_templates = DynamicModelMultipleChoiceField(
        queryset=DNSSECKeyTemplate.objects.all(),
        required=False,
        label=_("Key Templates"),
        help_text=_("Select CSK or KSK/ZSK templates for signing"),
        quick_add=True,
    )
    dnskey_ttl = TimePeriodField(
        required=False,
        label=_("DNSKEY TTL"),
        placeholder=DNSSECPolicy.get_fallback_setting("dnskey_ttl"),
    )
    purge_keys = TimePeriodField(
        required=False,
        label=_("Purge Keys"),
        placeholder=DNSSECPolicy.get_fallback_setting("purge_keys"),
    )
    publish_safety = TimePeriodField(
        required=False,
        label=_("Publish Safety"),
        placeholder=DNSSECPolicy.get_fallback_setting("publish_safety"),
    )
    retire_safety = TimePeriodField(
        required=False,
        label=_("Retire Safety"),
        placeholder=DNSSECPolicy.get_fallback_setting("retire_safety"),
    )
    signatures_jitter = TimePeriodField(
        required=False,
        label=_("Signatures Jitter"),
        placeholder=DNSSECPolicy.get_fallback_setting("signatures_jitter"),
    )
    signatures_refresh = TimePeriodField(
        required=False,
        label=_("Signatures Refresh"),
        placeholder=DNSSECPolicy.get_fallback_setting("signatures_refresh"),
    )
    signatures_validity = TimePeriodField(
        required=False,
        label=_("Signatures Validity"),
        placeholder=DNSSECPolicy.get_fallback_setting("signatures_validity"),
    )
    signatures_validity_dnskey = TimePeriodField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
        placeholder=DNSSECPolicy.get_fallback_setting("signatures_validity_dnskey"),
    )
    max_zone_ttl = TimePeriodField(
        required=False,
        label=_("Max Zone TTL"),
        placeholder=DNSSECPolicy.get_fallback_setting("max_zone_ttl"),
    )
    zone_propagation_delay = TimePeriodField(
        required=False,
        label=_("Zone Propagation Delay"),
        placeholder=DNSSECPolicy.get_fallback_setting("zone_propagation_delay"),
    )
    parent_ds_ttl = TimePeriodField(
        required=False,
        label=_("Parent DS TTL"),
        placeholder=DNSSECPolicy.get_fallback_setting("parent_ds_ttl"),
    )
    parent_propagation_delay = TimePeriodField(
        required=False,
        label=_("Parent Propagation Delay"),
        placeholder=DNSSECPolicy.get_fallback_setting("parent_propagation_delay"),
    )
    nsec3_opt_out = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("NSEC3 Opt-Out"),
    )

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        if not self.cleaned_data.get("use_nsec3"):
            self.cleaned_data["nsec3_iterations"] = None
            self.cleaned_data["nsec3_opt_out"] = None
            self.cleaned_data["nsec3_salt_size"] = None

        return self.cleaned_data


class DNSSECPolicyFilterForm(TenancyFilterForm, PrimaryModelFilterSetForm):
    model = DNSSECPolicy

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
            "owner_id",
        ),
        FieldSet(
            "name",
            "description",
            "status",
            "key_template_id",
            "inline_signing",
            name=_("Attributes"),
        ),
        FieldSet(
            "zone_id",
            "zone_template_id",
            name=_("Assignments"),
        ),
        FieldSet(
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            name=_("Timing"),
        ),
        FieldSet(
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            name=_("Parent Delegation"),
        ),
        FieldSet(
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            name=_("Proof of Non-Existence"),
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name=_("Tenancy"),
        ),
    )

    name = forms.CharField(
        required=False,
        label=_("Template Name"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    status = forms.MultipleChoiceField(
        choices=DNSSECPolicyStatusChoices,
        required=False,
        label=_("Status"),
    )
    inline_signing = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Use Inline Signing"),
    )
    key_template_id = DynamicModelMultipleChoiceField(
        queryset=DNSSECKeyTemplate.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Key Templates"),
    )
    zone_id = DynamicModelMultipleChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Zones"),
    )
    zone_template_id = DynamicModelMultipleChoiceField(
        queryset=ZoneTemplate.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Zone Templates"),
    )
    dnskey_ttl = TimePeriodField(
        required=False,
        label=_("DNSKEY TTL"),
    )
    purge_keys = TimePeriodField(
        required=False,
        label=_("Purge Keys"),
    )
    publish_safety = TimePeriodField(
        required=False,
        label=_("Publish Safety"),
    )
    retire_safety = TimePeriodField(
        required=False,
        label=_("Retire Safety"),
    )
    signatures_jitter = TimePeriodField(
        required=False,
        label=_("Signatures Jitter"),
    )
    signatures_refresh = TimePeriodField(
        required=False,
        label=_("Signatures Refresh"),
    )
    signatures_validity = TimePeriodField(
        required=False,
        label=_("Signatures Validity"),
    )
    signatures_validity_dnskey = TimePeriodField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = TimePeriodField(
        required=False,
        label=_("Max Zone TTL"),
    )
    zone_propagation_delay = TimePeriodField(
        required=False,
        label=_("Zone Propagation Delay"),
    )
    create_cdnskey = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Create CDNSKEY"),
    )
    cds_digest_types = forms.MultipleChoiceField(
        required=False,
        choices=DNSSECPolicyDigestChoices,
        label=_("CDS Digest Types"),
    )
    parent_ds_ttl = TimePeriodField(
        required=False,
        label=_("Parent DS TTL"),
    )
    parent_propagation_delay = TimePeriodField(
        required=False,
        label=_("Parent Propagation Delay"),
    )
    use_nsec3 = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Use NSEC3"),
    )
    nsec3_iterations = forms.IntegerField(
        required=False,
        label=_("NSEC3 Iterations"),
    )
    nsec3_opt_out = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("NSEC3 Opt-Out"),
    )
    nsec3_salt_size = forms.IntegerField(
        required=False,
        label=_("NSEC3 Salt Size"),
    )
    tag = TagFilterField(model)


class DNSSECPolicyImportForm(PrimaryModelImportForm):
    class Meta:
        model = DNSSECPolicy

        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "inline_signing",
            "key_templates",
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            "tenant",
            "tags",
        )

    status = CSVChoiceField(
        choices=DNSSECPolicyStatusChoices,
        required=False,
        label=_("Status"),
    )
    inline_signing = forms.BooleanField(
        required=False,
        label=_("Use Inline Signing"),
    )
    dnskey_ttl = TimePeriodField(
        required=False,
        label=_("DNSKEY TTL"),
    )
    purge_keys = TimePeriodField(
        required=False,
        label=_("Purge Keys"),
    )
    publish_safety = TimePeriodField(
        required=False,
        label=_("Publish Safety"),
    )
    retire_safety = TimePeriodField(
        required=False,
        label=_("Retire Safety"),
    )
    signatures_jitter = TimePeriodField(
        required=False,
        label=_("Signatures Jitter"),
    )
    signatures_refresh = TimePeriodField(
        required=False,
        label=_("Signatures Refresh"),
    )
    signatures_validity = TimePeriodField(
        required=False,
        label=_("Signatures Validity"),
    )
    signatures_validity_dnskey = TimePeriodField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = TimePeriodField(
        required=False,
        label=_("Max Zone TTL"),
    )
    zone_propagation_delay = TimePeriodField(
        required=False,
        label=_("Zone Propagation Delay"),
    )
    parent_ds_ttl = TimePeriodField(
        required=False,
        label=_("Parent DS TTL"),
    )
    parent_propagation_delay = TimePeriodField(
        required=False,
        label=_("Parent Propagation Delay"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )


class DNSSECPolicyBulkEditForm(PrimaryModelBulkEditForm):
    model = DNSSECPolicy

    fieldsets = (
        FieldSet(
            "description",
            "key_templates",
            "inline_signing",
            name=_("Attributes"),
        ),
        FieldSet(
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            name=_("Timing"),
        ),
        FieldSet(
            "create_cdnskey",
            "cds_digest_types",
            "parent_ds_ttl",
            "parent_propagation_delay",
            name=_("Parent Delegation"),
        ),
        FieldSet(
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
            name=_("Proof of Non-Existence"),
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
    )

    nullable_fields = (
        "description",
        "tenant",
        "dnskey_ttl",
        "purge_keys",
        "publish_safety",
        "retire_safety",
        "signatures_jitter",
        "signatures_refresh",
        "signatures_validity",
        "signatures_validity_dnskey",
        "max_zone_ttl",
        "zone_propagation_delay",
        "cds_digest_types",
        "parent_ds_ttl",
        "parent_propagation_delay",
        "nsec3_iterations",
        "nsec3_opt_out",
        "nsec3_salt_size",
        "cds_digest_types",
        "parent_ds_ttl",
        "parent_propagation_delay",
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(DNSSECPolicyStatusChoices),
        required=False,
        label=_("Status"),
    )
    inline_signing = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Use Inline Signing"),
    )
    dnskey_ttl = TimePeriodField(
        required=False,
        label=_("DNSKEY TTL"),
    )
    purge_keys = TimePeriodField(
        required=False,
        label=_("Purge Keys"),
    )
    publish_safety = TimePeriodField(
        required=False,
        label=_("Publish Safety"),
    )
    retire_safety = TimePeriodField(
        required=False,
        label=_("Retire Safety"),
    )
    signatures_jitter = TimePeriodField(
        required=False,
        label=_("Signatures Jitter"),
    )
    signatures_refresh = TimePeriodField(
        required=False,
        label=_("Signatures Refresh"),
    )
    signatures_validity = TimePeriodField(
        required=False,
        label=_("Signatures Validity"),
    )
    signatures_validity_dnskey = TimePeriodField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = TimePeriodField(
        required=False,
        label=_("Max Zone TTL"),
    )
    zone_propagation_delay = TimePeriodField(
        required=False,
        label=_("Zone Propagation Delay"),
    )
    create_cdnskey = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Create CDNSKEY"),
    )
    cds_digest_types = forms.MultipleChoiceField(
        choices=DNSSECPolicyDigestChoices,
        required=False,
        label=_("CDS Digest Types"),
    )
    parent_ds_ttl = TimePeriodField(
        required=False,
        label=_("Parent DS TTL"),
    )
    parent_propagation_delay = TimePeriodField(
        required=False,
        label=_("Parent Propagation Delay"),
    )
    use_nsec3 = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Use NSEC3"),
    )
    nsec3_iterations = forms.IntegerField(
        required=False,
        label=_("NSEC3 Iterations"),
    )
    nsec3_opt_out = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("NSEC3 Opt-Out"),
    )
    nsec3_salt_size = forms.IntegerField(
        required=False,
        label=_("NSEC3 Salt Size"),
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

    def clean_cds_digest_types(self, *args, **kwargs):
        if not (
            cds_digest_types := self.cleaned_data.get("cds_digest_types")
        ) and "cds_digest_types" not in self.data.get("_nullify", []):
            return self.initial.get("cds_digest_types")

        return cds_digest_types
