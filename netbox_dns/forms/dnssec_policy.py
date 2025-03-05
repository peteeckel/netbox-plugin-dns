from packaging.version import Version

from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    TagFilterField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from utilities.release import load_release_data
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate
from netbox_dns.choices import DNSSECPolicyDigestChoices


__all__ = (
    "DNSSECPolicyForm",
    "DNSSECPolicyFilterForm",
    "DNSSECPolicyImportForm",
    "DNSSECPolicyBulkEditForm",
)

QUICK_ADD = Version(load_release_data().version) >= Version("4.2.5")


class DNSSECPolicyForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "description", name=_("Attributes")),
        FieldSet(
            "key_templates",
            "inline_signing",
            name=_("Signing"),
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
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    key_templates = DynamicModelMultipleChoiceField(
        queryset=DNSSECKeyTemplate.objects.all(),
        required=False,
        label=_("Key Templates"),
        help_text=_("Select CSK or KSK/ZSK templates for signing"),
        quick_add=QUICK_ADD,
    )

    class Meta:
        model = DNSSECPolicy
        fields = (
            "name",
            "description",
            "key_templates",
            "inline_signing",
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


class DNSSECPolicyFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = DNSSECPolicy
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "description", name=_("Attributes")),
        FieldSet(
            "key_template_id",
            "inline_signing",
            name=_("Signing"),
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
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )

    key_template_id = DynamicModelMultipleChoiceField(
        queryset=DNSSECKeyTemplate.objects.all(),
        required=False,
        label=_("Key Templates"),
    )
    inline_signing = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
        label=_("Use Inline Signing"),
    )

    dnskey_ttl = forms.IntegerField(
        required=False,
        label=_("DNSKEY TTL"),
    )
    purge_keys = forms.IntegerField(
        required=False,
        label=_("Purge Keys"),
    )
    publish_safety = forms.IntegerField(
        required=False,
        label=_("Publish Safety"),
    )
    retire_safety = forms.IntegerField(
        required=False,
        label=_("Retire Safety"),
    )
    signatures_jitter = forms.IntegerField(
        required=False,
        label=_("Signatures Jitter"),
    )
    signatures_refresh = forms.IntegerField(
        required=False,
        label=_("Signatures Refresh"),
    )
    signatures_validity = forms.IntegerField(
        required=False,
        label=_("Signatures Validity"),
    )
    signatures_validity_dnskey = forms.IntegerField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = forms.IntegerField(
        required=False,
        label=_("Max Zone TTL"),
    )
    zone_propagation_delay = forms.IntegerField(
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
    parent_ds_ttl = forms.IntegerField(
        required=False,
        label=_("Parent DS TTL"),
    )
    parent_propagation_delay = forms.IntegerField(
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


    tag = TagFilterField(DNSSECPolicy)


class DNSSECPolicyImportForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )

    class Meta:
        model = DNSSECPolicy
        fields = (
            "name",
            "description",
            "key_templates",
            "inline_signing",
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


class DNSSECPolicyBulkEditForm(NetBoxModelBulkEditForm):
    model = DNSSECPolicy

    description = forms.CharField(
        max_length=200,
        required=False,
        label=_("Description"),
    )

    inline_signing = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Use Inline Signing"),
    )

    dnskey_ttl = forms.IntegerField(
        required=False,
        label=_("DNSKEY TTL"),
    )
    purge_keys = forms.IntegerField(
        required=False,
        label=_("Purge Keys"),
    )
    publish_safety = forms.IntegerField(
        required=False,
        label=_("Publish Safety"),
    )
    retire_safety = forms.IntegerField(
        required=False,
        label=_("Retire Safety"),
    )
    signatures_jitter = forms.IntegerField(
        required=False,
        label=_("Signatures Jitter"),
    )
    signatures_refresh = forms.IntegerField(
        required=False,
        label=_("Signatures Refresh"),
    )
    signatures_validity = forms.IntegerField(
        required=False,
        label=_("Signatures Validity"),
    )
    signatures_validity_dnskey = forms.IntegerField(
        required=False,
        label=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = forms.IntegerField(
        required=False,
        label=_("Max Zone TTL"),
    )
    zone_propagation_delay = forms.IntegerField(
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
    parent_ds_ttl = forms.IntegerField(
        required=False,
        label=_("Parent DS TTL"),
    )
    parent_propagation_delay = forms.IntegerField(
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

    fieldsets = (
        FieldSet(
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "key_templates",
            "inline_signing",
            name=_("Signing"),
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
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
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

    def clean(self):
        cleaned_data = super().clean()

        if not self.cleaned_data.get("cds_digest_types"):
            if "cds_digest_types" not in self.data.get("_nullify", []):
                self.cleaned_data["cds_digest_types"] = self.initial.get(
                    "cds_digest_types"
                )

        return cleaned_data
