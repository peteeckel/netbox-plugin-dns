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
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
)
from utilities.forms.widgets import BulkEditNullBooleanSelect
from utilities.forms import add_blank_choice
from utilities.forms.rendering import FieldSet
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm

from netbox_dns.models import RecordTemplate, ZoneTemplate
from netbox_dns.choices import RecordSelectableTypeChoices, RecordStatusChoices
from netbox_dns.utilities import name_to_unicode
from netbox_dns.fields import TimePeriodField


__all__ = (
    "RecordTemplateForm",
    "RecordTemplateFilterForm",
    "RecordTemplateImportForm",
    "RecordTemplateBulkEditForm",
)


class RecordTemplateForm(TenancyForm, NetBoxModelForm):
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
            "tenant_group",
            "tenant",
            "tags",
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
            name=_("Record Template"),
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

        initial_record_name = self.initial.get("record_name")
        if initial_record_name:
            self.initial["record_name"] = name_to_unicode(initial_record_name)

    type = forms.ChoiceField(
        choices=add_blank_choice(RecordSelectableTypeChoices),
        required=True,
        label=_("Type"),
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label=_("Disable PTR"),
    )
    ttl = TimePeriodField(
        required=False,
        label=_("TTL"),
    )


class RecordTemplateFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = RecordTemplate

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "zone_template_id",
            name=_("Zone Templates"),
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name=_("Tenancy"),
        ),
    )

    type = forms.MultipleChoiceField(
        choices=RecordSelectableTypeChoices,
        required=False,
        label=_("Type"),
    )
    name = forms.CharField(
        required=False,
        label=_("Template Name"),
    )
    record_name = forms.CharField(
        required=False,
        label=_("Name"),
    )
    value = forms.CharField(
        required=False,
        label=_("Value"),
    )
    status = forms.MultipleChoiceField(
        choices=RecordStatusChoices,
        required=False,
        label=_("Status"),
    )
    ttl = TimePeriodField(
        required=False,
        label=_("TTL"),
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        label=_("Disable PTR"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
    )
    zone_template_id = DynamicModelMultipleChoiceField(
        queryset=ZoneTemplate.objects.all(),
        required=False,
        null_option=_("None"),
        label=_("Zone Templates"),
    )
    tag = TagFilterField(RecordTemplate)


class RecordTemplateImportForm(NetBoxModelImportForm):
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

    type = CSVChoiceField(
        choices=RecordSelectableTypeChoices,
        required=True,
        label=_("Type"),
    )
    status = CSVChoiceField(
        choices=RecordStatusChoices,
        required=False,
        label=_("Status"),
    )
    ttl = TimePeriodField(
        required=False,
        label=_("TTL"),
    )
    disable_ptr = forms.BooleanField(
        required=False,
        label=_("Disable PTR"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )


class RecordTemplateBulkEditForm(NetBoxModelBulkEditForm):
    model = RecordTemplate

    fieldsets = (
        FieldSet(
            "record_name",
            "type",
            "value",
            "status",
            "ttl",
            "disable_ptr",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
    )

    nullable_fields = (
        "description",
        "ttl",
        "tenant",
    )

    record_name = forms.CharField(
        required=False,
        label=_("Record Name"),
    )
    type = forms.ChoiceField(
        choices=add_blank_choice(RecordSelectableTypeChoices),
        required=False,
        label=_("Type"),
    )
    value = forms.CharField(
        required=False,
        label=_("Value"),
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(RecordStatusChoices),
        required=False,
        label=_("Status"),
    )
    ttl = TimePeriodField(
        required=False,
        label=_("TTL"),
    )
    disable_ptr = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label=_("Disable PTR"),
    )
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
