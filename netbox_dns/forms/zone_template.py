from django import forms
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    TagFilterField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    NameServer,
    Registrar,
    RegistrationContact,
)


__all__ = (
    "ZoneTemplateForm",
    "ZoneTemplateFilterForm",
    "ZoneTemplateImportForm",
    "ZoneTemplateBulkEditForm",
)


class ZoneTemplateForm(TenancyForm, NetBoxModelForm):
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
    )
    record_templates = DynamicModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        required=False,
    )

    fieldsets = (
        FieldSet("name", "description", "nameservers", name=_("Zone Template")),
        FieldSet("record_templates", name=_("Record Templates")),
        FieldSet(
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name=_("Domain Registration"),
        ),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet("tags", name=_("Tags")),
    )

    class Meta:
        model = ZoneTemplate

        fields = (
            "name",
            "nameservers",
            "record_templates",
            "description",
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant_group",
            "tenant",
            "tags",
        )


class ZoneTemplateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = ZoneTemplate
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "nameserver_id", "description", name=_("Attributes")),
        FieldSet("record_template_id", name=_("Record Templates")),
        FieldSet(
            "registrar_id",
            "registrant_id",
            "admin_c_id",
            "tech_c_id",
            "billing_c_id",
            name=_("Registration"),
        ),
        FieldSet("tenant_group_id", "tenant_id", name=_("Tenancy")),
    )

    name = forms.CharField(
        required=False,
        label=_("Template Name"),
    )
    nameserver_id = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("Nameservers"),
    )
    record_template_id = DynamicModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        required=False,
        label=_("Record Templates"),
    )
    description = forms.CharField(
        required=False,
    )
    registrar_id = DynamicModelMultipleChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label=_("Registrar"),
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
    tag = TagFilterField(ZoneTemplate)


class ZoneTemplateImportForm(NetBoxModelImportForm):
    nameservers = CSVModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Nameservers"),
    )
    record_templates = CSVModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Record Remplates"),
    )
    registrar = CSVModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        to_field_name="name",
        error_messages={
            "invalid_choice": _("Registrar %(value)s not found"),
        },
        label=_("Registrar"),
    )
    registrant = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Registrant contact ID %(value)s not found"),
        },
        label=_("Registrant"),
    )
    admin_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Administrative contact ID %(value)s not found"),
        },
        label=_("Administrative Contact"),
    )
    tech_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Technical contact ID %(value)s not found"),
        },
        label=_("Technical Contact"),
    )
    billing_c = CSVModelChoiceField(
        queryset=RegistrationContact.objects.all(),
        required=False,
        to_field_name="contact_id",
        error_messages={
            "invalid_choice": _("Billing contact ID %(value)s not found"),
        },
        label=_("Billing Contact"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        label=_("Tenant"),
    )

    class Meta:
        model = ZoneTemplate

        fields = (
            "name",
            "nameservers",
            "record_templates",
            "description",
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant",
            "tags",
        )


class ZoneTemplateBulkEditForm(NetBoxModelBulkEditForm):
    nameservers = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label=_("Nameservers"),
    )
    record_templates = DynamicModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        required=False,
        label=_("Record Templates"),
    )
    description = forms.CharField(max_length=200, required=False)
    registrar = DynamicModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label=_("Registrar"),
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

    model = ZoneTemplate

    fieldsets = (
        FieldSet(
            "nameservers",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "record_templates",
            name=_("Record Templates"),
        ),
        FieldSet(
            "registrar",
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
        "record_templates",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
        "tenant",
    )
