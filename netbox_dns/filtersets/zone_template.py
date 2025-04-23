import django_filters

from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import (
    ZoneTemplate,
    RecordTemplate,
    Registrar,
    RegistrationContact,
    NameServer,
    DNSSECPolicy,
)


__all__ = ("ZoneTemplateFilterSet",)


class ZoneTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = ZoneTemplate

        fields = (
            "id",
            "name",
            "description",
            "soa_rname",
        )

    record_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RecordTemplate.objects.all(),
        field_name="record_templates",
        to_field_name="id",
        label=_("Record Template ID"),
    )
    record_template = django_filters.ModelMultipleChoiceFilter(
        queryset=RecordTemplate.objects.all(),
        field_name="record_templates__name",
        to_field_name="name",
        label=_("Record Template"),
    )
    nameserver_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="nameservers",
        to_field_name="id",
        label=_("Nameservers ID"),
    )
    nameserver = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="nameservers__name",
        to_field_name="name",
        label=_("Nameserver"),
    )
    soa_mname_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="soa_mname",
        to_field_name="id",
        label=_("SOA MName ID"),
    )
    soa_mname = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        field_name="soa_mname__name",
        to_field_name="name",
        label=_("SOA MName"),
    )
    dnssec_policy_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DNSSECPolicy.objects.all(),
        label=_("DNSSEC Policy ID"),
    )
    dnssec_policy = django_filters.ModelMultipleChoiceFilter(
        queryset=DNSSECPolicy.objects.all(),
        field_name="dnssec_policy__name",
        to_field_name="name",
        label=_("DNSSEC Policy"),
    )
    registrar_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        label=_("Registrar ID"),
    )
    registrar = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        field_name="registrar__name",
        to_field_name="name",
        label=_("Registrar"),
    )
    registrant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Registrant ID"),
    )
    registrant = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        field_name="registrant__contact_id",
        to_field_name="contact_id",
        label=_("Registrant"),
    )
    admin_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Administrative Contact ID"),
    )
    admin_c = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        field_name="admin_c__contact_id",
        to_field_name="contact_id",
        label=_("Administrative Contact"),
    )
    tech_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Technical Contact ID"),
    )
    tech_c = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        field_name="tech_c__contact_id",
        to_field_name="contact_id",
        label=_("Technical Contact"),
    )
    billing_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Billing Contact ID"),
    )
    billing_c = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        field_name="billing_c__contact_id",
        to_field_name="contact_id",
        label=_("Billing Contact"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(soa_rname__icontains=value)
            | Q(registrar__name__icontains=value)
            | Q(registry_domain_id__icontains=value)
            | Q(registrant__name__icontains=value)
            | Q(admin_c__name__icontains=value)
            | Q(tech_c__name__icontains=value)
            | Q(billing_c__name__icontains=value)
        )
        return queryset.filter(qs_filter)
