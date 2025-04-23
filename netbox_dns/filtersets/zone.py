import netaddr
from netaddr.core import AddrFormatError

import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_dns.models import (
    View,
    Zone,
    Registrar,
    RegistrationContact,
    NameServer,
    DNSSECPolicy,
)
from netbox_dns.choices import ZoneStatusChoices, ZoneEPPStatusChoices


__all__ = ("ZoneFilterSet",)


class ZoneFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = Zone

        fields = (
            "id",
            "name",
            "description",
            "default_ttl",
            "soa_ttl",
            "soa_rname",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "soa_serial_auto",
            "rfc2317_parent_managed",
            "inline_signing",
            "registry_domain_id",
            "domain_status",
        )

    status = django_filters.MultipleChoiceFilter(
        choices=ZoneStatusChoices,
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        label=_("View ID"),
    )
    view = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="view__name",
        to_field_name="name",
        label=_("View"),
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
    parental_agents = MultiValueCharFilter(
        method="filter_parental_agents",
        label=_("Parental Agents"),
    )
    rfc2317_prefix = MultiValueCharFilter(
        method="filter_rfc2317_prefix",
        label=_("RFC2317 Prefix"),
    )
    rfc2317_parent_zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        field_name="rfc2317_parent_zone",
        to_field_name="id",
        label=_("RFC2317 Parent Zone"),
    )
    rfc2317_parent_zone = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        field_name="rfc2317_parent_zone__name",
        to_field_name="name",
        label=_("RFC2317 Parent Zone"),
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
    expiration_date = django_filters.DateFromToRangeFilter()
    domain_status = django_filters.MultipleChoiceFilter(
        choices=ZoneEPPStatusChoices,
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
    arpa_network = MultiValueCharFilter(
        method="filter_arpa_network",
        label=_("ARPA Network"),
    )
    active = django_filters.BooleanFilter(
        label=_("Zone is active"),
    )

    def filter_parental_agents(self, queryset, name, value):
        if not value:
            return queryset

        query_values = []
        for v in value:
            try:
                query_values.append(str(netaddr.IPAddress(v)))
            except (AddrFormatError, ValueError):
                pass

        return queryset.filter(parental_agents__overlap=query_values)

    def filter_arpa_network(self, queryset, name, value):
        if not value:
            return queryset
        try:
            arpa_networks = [
                str(netaddr.IPNetwork(item)) for item in value if item.strip()
            ]
            if not arpa_networks:
                return queryset
            return queryset.filter(arpa_network__in=arpa_networks)

        except (netaddr.AddrFormatError, ValueError):
            return queryset.none()

    def filter_rfc2317_prefix(self, queryset, name, value):
        if not value:
            return queryset
        try:
            rfc2317_prefixes = [
                str(netaddr.IPNetwork(item)) for item in value if item.strip()
            ]
            if not rfc2317_prefixes:
                return queryset
            return queryset.filter(rfc2317_prefix__in=rfc2317_prefixes)

        except (netaddr.AddrFormatError, ValueError):
            return queryset.none()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(status__icontains=value)
            | Q(view__name__icontains=value)
            | Q(dnssec_policy__name__icontains=value)
            | Q(registrar__name__icontains=value)
            | Q(registry_domain_id__icontains=value)
            | Q(registrant__name__icontains=value)
            | Q(admin_c__name__icontains=value)
            | Q(tech_c__name__icontains=value)
            | Q(billing_c__name__icontains=value)
        )
        return queryset.filter(qs_filter)
