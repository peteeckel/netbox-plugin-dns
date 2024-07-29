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
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms import add_blank_choice
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import RecordTemplate, ZoneTemplate
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices
from netbox_dns.utilities import name_to_unicode


__all__ = (
    "RecordTemplateForm",
    "RecordTemplateFilterForm",
    "RecordTemplateImportForm",
    "RecordTemplateBulkEditForm",
)


class RecordTemplateForm(TenancyForm, NetBoxModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_record_name = self.initial.get("record_name")
        if initial_record_name:
            self.initial["record_name"] = name_to_unicode(initial_record_name)

    disable_ptr = forms.BooleanField(
        label="Disable PTR",
        required=False,
    )
    ttl = forms.IntegerField(
        required=False,
        label="TTL",
    )

    fieldsets = (
        FieldSet(
            "name",
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name="Record Template",
        ),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
        FieldSet("tags", name="Tags"),
    )

    class Meta:
        model = RecordTemplate

        fields = (
            "name",
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            "tags",
            "tenant",
        )


class RecordTemplateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = RecordTemplate
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "record_name",
            "type",
            "value",
            "status",
            "disable_ptr",
            "status",
            "description",
            name="Attributes",
        ),
        FieldSet("zone_template_id", name="Zone Templates"),
        FieldSet("tenant_group_id", "tenant_id", name="Tenancy"),
    )

    type = forms.MultipleChoiceField(
        choices=RecordTypeChoices,
        required=False,
    )
    name = forms.CharField(
        required=False,
        label="Template name",
    )
    record_name = forms.CharField(
        required=False,
        label="Name",
    )
    value = forms.CharField(
        required=False,
    )
    status = forms.MultipleChoiceField(
        choices=RecordStatusChoices,
        required=False,
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        label="Disable PTR",
    )
    description = forms.CharField(
        required=False,
    )
    zone_template_id = DynamicModelMultipleChoiceField(
        queryset=ZoneTemplate.objects.all(),
        required=False,
        label="Zone templates",
    )
    tag = TagFilterField(RecordTemplate)


class RecordTemplateImportForm(NetBoxModelImportForm):
    type = CSVChoiceField(
        choices=RecordTypeChoices,
        required=True,
        help_text="Record Type",
    )
    status = CSVChoiceField(
        choices=RecordStatusChoices,
        required=False,
        help_text="Record status",
    )
    ttl = forms.IntegerField(
        required=False,
        help_text="TTL",
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label="Disable PTR",
        help_text="Disable generation of a PTR record",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        help_text="Assigned tenant",
    )

    class Meta:
        model = RecordTemplate

        fields = (
            "name",
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            "tenant",
            "tags",
        )


class RecordTemplateBulkEditForm(NetBoxModelBulkEditForm):
    model = RecordTemplate

    type = forms.ChoiceField(
        choices=add_blank_choice(RecordTypeChoices),
        required=False,
    )
    value = forms.CharField(
        required=False,
        label="Value",
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RecordStatusChoices),
        required=False,
    )
    ttl = forms.IntegerField(
        required=False,
        label="TTL",
    )
    disable_ptr = forms.NullBooleanField(
        required=False, widget=BulkEditNullBooleanSelect(), label="Disable PTR"
    )
    description = forms.CharField(max_length=200, required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    fieldsets = (
        FieldSet(
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name="Attributes",
        ),
        FieldSet("tenant_group", "tenant", name="Tenancy"),
    )
    nullable_fields = ("description", "ttl", "tenant")
