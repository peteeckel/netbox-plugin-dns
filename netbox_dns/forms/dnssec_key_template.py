from django import forms
from django.contrib.postgres.forms import SimpleArrayField
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
from utilities.forms.rendering import FieldSet
from utilities.forms import add_blank_choice
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import DNSSECKeyTemplate, DNSSECPolicy
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)
from netbox_dns.fields import TimePeriodField


__all__ = (
    "DNSSECKeyTemplateForm",
    "DNSSECKeyTemplateFilterForm",
    "DNSSECKeyTemplateImportForm",
    "DNSSECKeyTemplateBulkEditForm",
)


class DNSSECKeyTemplateForm(TenancyForm, NetBoxModelForm):
    class Meta:
        model = DNSSECKeyTemplate

        fields = (
            "name",
            "description",
            "type",
            "lifetime",
            "key_size",
            "algorithm",
            "tenant_group",
            "tenant",
            "tags",
        )

    fieldsets = (
        FieldSet(
            "name",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            name=_("Key Properties"),
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

    lifetime = TimePeriodField(
        required=False,
    )


class DNSSECKeyTemplateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = DNSSECKeyTemplate

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "policiy_id",
            name=_("Policies"),
        ),
        FieldSet(
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            name=_("Key Properties"),
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name=_("Tenancy"),
        ),
    )

    name = forms.CharField(
        required=False,
    )
    description = forms.CharField(
        required=False,
    )
    policy_id = DynamicModelMultipleChoiceField(
        queryset=DNSSECPolicy.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Policies"),
    )
    type = forms.MultipleChoiceField(
        choices=DNSSECKeyTemplateTypeChoices,
        required=False,
    )
    lifetime = SimpleArrayField(
        base_field=forms.IntegerField(),
        required=False,
        help_text=_("Enter a list of integer lifetime values, separated by comma (,)"),
    )
    algorithm = forms.MultipleChoiceField(
        choices=DNSSECKeyTemplateAlgorithmChoices,
        required=False,
    )
    key_size = SimpleArrayField(
        base_field=forms.ChoiceField(
            choices=DNSSECKeyTemplateKeySizeChoices,
        ),
        required=False,
        help_text=_("Enter a list of integer key sizes, separated by comma (,)"),
    )
    tag = TagFilterField(DNSSECKeyTemplate)


class DNSSECKeyTemplateImportForm(NetBoxModelImportForm):
    class Meta:
        model = DNSSECKeyTemplate

        fields = (
            "name",
            "description",
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            "tenant",
            "tags",
        )

    lifetime = TimePeriodField(
        required=False,
        label=_("Lifetime"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )


class DNSSECKeyTemplateBulkEditForm(NetBoxModelBulkEditForm):
    model = DNSSECKeyTemplate

    fieldsets = (
        FieldSet(
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "type",
            "lifetime",
            "algorithm",
            "key_size",
            name=_("Key Properties"),
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
        "lifetime",
        "key_size",
    )

    description = forms.CharField(
        max_length=200,
        required=False,
        label=_("Description"),
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(DNSSECKeyTemplateTypeChoices),
        required=False,
        label=_("Key Type"),
    )
    lifetime = TimePeriodField(
        required=False,
        label=_("Lifetime"),
    )
    algorithm = forms.ChoiceField(
        choices=add_blank_choice(DNSSECKeyTemplateAlgorithmChoices),
        required=False,
        label=_("Algorithm"),
    )
    key_size = forms.ChoiceField(
        choices=add_blank_choice(DNSSECKeyTemplateKeySizeChoices),
        required=False,
        label=_("Key Size"),
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
