import django_filters

from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    Registrar,
    Contact,
    NameServer,
)


__all__ = ("ZoneTemplateFilterSet",)


class ZoneTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    record_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RecordTemplate.objects.all(),
        field_name="record_templates",
        to_field_name="id",
        label="Record Template ID",
    )
    record_template = django_filters.ModelMultipleChoiceFilter(
        queryset=RecordTemplate.objects.all(),
        field_name="record_templates__name",
        to_field_name="name",
        label="Record Template",
    )
    nameserver_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="nameservers",
        to_field_name="id",
        label="Nameservers ID",
    )
    nameserver = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="nameservers__name",
        to_field_name="name",
        label="Nameserver",
    )
    registrar_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        label="Registrar ID",
    )
    registrar = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        field_name="registrar__name",
        to_field_name="name",
        label="Registrar",
    )
    registrant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Registrant ID",
    )
    registrant = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="registrant__contact_id",
        to_field_name="contact_id",
        label="Registrant",
    )
    admin_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Administrative Contact ID",
    )
    admin_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="admin_c__contact_id",
        to_field_name="contact_id",
        label="Administrative Contact",
    )
    tech_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Technical Contact ID",
    )
    tech_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="tech_c__contact_id",
        to_field_name="contact_id",
        label="Technical Contact",
    )
    billing_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Billing Contact ID",
    )
    billing_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="billing_c__contact_id",
        to_field_name="contact_id",
        label="Billing Contact",
    )

    class Meta:
        model = ZoneTemplate
        fields = (
            "id",
            "name",
            "description",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(registrar__name__icontains=value)
            | Q(registry_domain_id__icontains=value)
            | Q(registrant__name__icontains=value)
            | Q(admin_c__name__icontains=value)
            | Q(tech_c__name__icontains=value)
            | Q(billing_c__name__icontains=value)
        )
        return queryset.filter(qs_filter)
