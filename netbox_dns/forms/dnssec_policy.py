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
from utilities.forms.rendering import FieldSet, TabbedGroups
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import DNSSECPolicy, DNSSECKey
from netbox_dns.choices import DNSSECKeyTypeChoices


__all__ = (
    "DNSSECPolicyForm",
    "DNSSECPolicyFilterForm",
    "DNSSECPolicyImportForm",
    "DNSSECPolicyBulkEditForm",
)


class DNSSECPolicyForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "description", name=_("Attributes")),
        FieldSet(
            "keys",
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
            name=_("NSEC"),
        ),
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    keys = DynamicModelMultipleChoiceField(
        queryset=DNSSECKey.objects.all(),
        required=False,
        label=_("Signing Keys"),
        help_text=_("Select CSK or KSK/CSK for signing"),
        quick_add=True,
    )

    class Meta:
        model = DNSSECPolicy
        fields = (
            "name",
            "description",
            "keys",
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
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
    )

    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
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
            "keys",
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
            "keys",
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
            name=_("NSEC"),
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
