from django import forms

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
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    NameServer,
    Registrar,
    Contact,
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
        FieldSet("name", "description", "nameservers", name="Zone Template"),
        FieldSet("record_templates", name="Record Templates"),
        FieldSet(
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            name="Domain Registration",
        ),
        FieldSet("tags", name="Tags"),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
    )

    class Meta:
        model = ZoneTemplate

        fields = (
            "name",
            "nameservers",
            "record_templates",
            "description",
            "tags",
            "registrar",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "tenant",
        )


class ZoneTemplateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = ZoneTemplate
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("name", "nameserver_id", "description", name="Attributes"),
        FieldSet("record_template_id", name="Record Templates"),
        FieldSet(
            "registrar_id",
            "registrant_id",
            "admin_c_id",
            "tech_c_id",
            "billing_c_id",
            name="Registration",
        ),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    name = forms.CharField(
        required=False,
        label="Template name",
    )
    nameserver_id = DynamicModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        required=False,
        label="Nameservers",
    )
    record_template_id = DynamicModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        required=False,
        label="Record templates",
    )
    description = forms.CharField(
        required=False,
    )
    registrar_id = DynamicModelMultipleChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
        label="Registrar",
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
    tag = TagFilterField(ZoneTemplate)


class ZoneTemplateImportForm(NetBoxModelImportForm):
    nameservers = CSVModelMultipleChoiceField(
        queryset=NameServer.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Name servers for the zone template",
    )
    record_templates = CSVModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Record templates used by this zone template",
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
    )
    record_templates = DynamicModelMultipleChoiceField(
        queryset=RecordTemplate.objects.all(),
        required=False,
    )
    description = forms.CharField(max_length=200, required=False)
    registrar = DynamicModelChoiceField(
        queryset=Registrar.objects.all(),
        required=False,
    )
    registrant = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
    )
    admin_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Administrative Contact",
    )
    tech_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Technical Contact",
    )
    billing_c = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Billing Contact",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    model = ZoneTemplate

    fieldsets = (
        FieldSet(
            "nameservers",
            "description",
            name="Attributes",
        ),
        FieldSet(
            "record_templates",
            name="Record Templates",
        ),
        FieldSet(
            "registrar",
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
        "nameservers",
        "record_templates",
        "registrar",
        "registrant",
        "admin_c",
        "tech_c",
        "billing_c",
    )
