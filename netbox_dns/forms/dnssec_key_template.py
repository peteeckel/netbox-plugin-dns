from django import forms
from django.contrib.postgres.forms import SimpleArrayField
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
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import HTMXSelect
from utilities.forms import add_blank_choice, get_field_value
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


class DNSSECKeyTemplateForm(TenancyForm, PrimaryModelForm):
    class Meta:
        model = DNSSECKeyTemplate

        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "type",
            "lifetime",
            "key_size",
            "algorithm",
            "tenant_group",
            "tenant",
            "tags",
        )

        widgets = {
            "algorithm": HTMXSelect(),
        }

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        algorithm = get_field_value(self, "algorithm")
        if algorithm != DNSSECKeyTemplateAlgorithmChoices.RSASHA256:
            del self.fields["key_size"]

    lifetime = TimePeriodField(
        required=False,
        label=_("Lifetime"),
    )


class DNSSECKeyTemplateFilterForm(TenancyFilterForm, PrimaryModelFilterSetForm):
    model = DNSSECKeyTemplate

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
            name=_("Attributes"),
        ),
        FieldSet(
            "policy_id",
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
        label=_("Template Name"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    policy_id = DynamicModelMultipleChoiceField(
        queryset=DNSSECPolicy.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Policy"),
    )
    type = forms.MultipleChoiceField(
        choices=DNSSECKeyTemplateTypeChoices,
        required=False,
        label=_("Type"),
    )
    lifetime = TimePeriodField(
        label=_("Lifetime"),
    )
    algorithm = forms.MultipleChoiceField(
        choices=DNSSECKeyTemplateAlgorithmChoices,
        required=False,
        label=_("Algorithm"),
    )
    key_size = SimpleArrayField(
        base_field=forms.ChoiceField(
            choices=DNSSECKeyTemplateKeySizeChoices,
        ),
        required=False,
        help_text=_("Enter a list of integer key sizes, separated by comma (,)"),
    )
    tag = TagFilterField(model)


class DNSSECKeyTemplateImportForm(PrimaryModelImportForm):
    class Meta:
        model = DNSSECKeyTemplate

        fields = (
            "name",
            "description",
            "owner",
            "comments",
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


class DNSSECKeyTemplateBulkEditForm(PrimaryModelBulkEditForm):
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
        "lifetime",
        "key_size",
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
