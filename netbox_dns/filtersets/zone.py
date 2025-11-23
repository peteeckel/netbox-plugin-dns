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
            "default_ttl",
            "soa_ttl",
            "soa_serial",
            "soa_refresh",
            "soa_retry",
            "soa_expire",
            "soa_minimum",
            "soa_serial_auto",
            "rfc2317_parent_managed",
            "registry_domain_id",
            "domain_status",
            "inline_signing",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=ZoneStatusChoices,
    )

    view = django_filters.ModelMultipleChoiceFilter(
        field_name="view__name",
        queryset=View.objects.all(),
        to_field_name="name",
        label=_("View (name)"),
    )
    view_name = django_filters.CharFilter(
        field_name="view__name",
        label=_("View (name)"),
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        label=_("View (ID)"),
    )

    nameserver = django_filters.ModelMultipleChoiceFilter(
        field_name="nameservers__name",
        queryset=NameServer.objects.all(),
        to_field_name="name",
        label=_("Nameserver (name)"),
    )
    nameserver_name = django_filters.CharFilter(
        field_name="nameservers__name",
        distinct=True,
        label=_("Nameserver (name)"),
    )
    nameserver_id = django_filters.ModelMultipleChoiceFilter(
        field_name="nameservers",
        queryset=NameServer.objects.all(),
        label=_("Nameserver (ID)"),
    )

    soa_mname = django_filters.ModelMultipleChoiceFilter(
        field_name="soa_mname__name",
        queryset=NameServer.objects.all(),
        to_field_name="name",
        label=_("SOA MName (name)"),
    )
    soa_mname_name = django_filters.CharFilter(
        field_name="soa_mname__name",
        label=_("SOA MName (name)"),
    )
    soa_mname_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NameServer.objects.all(),
        label=_("SOA MName (ID)"),
    )

    soa_rname = django_filters.CharFilter(
        label=_("SOA RName"),
    )

    dnssec_policy = django_filters.ModelMultipleChoiceFilter(
        field_name="dnssec_policy__name",
        queryset=DNSSECPolicy.objects.all(),
        to_field_name="name",
        label=_("DNSSEC Policy (name)"),
    )
    dnssec_policy_name = django_filters.CharFilter(
        field_name="dnssec_policy__name",
        label=_("DNSSEC Policy (name)"),
    )
    dnssec_policy_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DNSSECPolicy.objects.all(),
        label=_("DNSSEC Policy (ID)"),
    )

    parental_agents = MultiValueCharFilter(
        method="filter_parental_agents",
        label=_("Parental Agents"),
    )
    rfc2317_prefix = MultiValueCharFilter(
        method="filter_rfc2317_prefix",
        label=_("RFC2317 Prefix"),
    )

    rfc2317_parent_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="rfc2317_parent_zone__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("RFC2317 Parent Zone (name)"),
    )
    rfc2317_parent_zone_name = django_filters.CharFilter(
        field_name="rfc2317_parent_zone__name",
        label=_("RFC2317 Parent Zone (name)"),
    )
    rfc2317_parent_zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        label=_("RFC2317 Parent Zone (ID)"),
    )

    registrar = django_filters.ModelMultipleChoiceFilter(
        field_name="registrar__name",
        queryset=Registrar.objects.all(),
        to_field_name="name",
        label=_("Registrar (name)"),
    )
    registrar_name = django_filters.CharFilter(
        field_name="registrar__name",
        label=_("Registrar (name)"),
    )
    registrar_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        label=_("Registrar (ID)"),
    )

    expiration_date = django_filters.DateFromToRangeFilter(
        label=_("Expiration Date"),
    )
    domain_status = django_filters.MultipleChoiceFilter(
        choices=ZoneEPPStatusChoices,
        label=_("Domain Status"),
    )

    registrant = django_filters.ModelMultipleChoiceFilter(
        field_name="registrant__contact_id",
        queryset=RegistrationContact.objects.all(),
        to_field_name="contact_id",
        label=_("Registrant (contact_id)"),
    )
    registrant_contact_id = django_filters.CharFilter(
        field_name="registrant__contact_id",
        label=_("Registrant (contact_id)"),
    )
    registrant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Registrant (ID)"),
    )

    admin_c = django_filters.ModelMultipleChoiceFilter(
        field_name="admin_c__contact_id",
        queryset=RegistrationContact.objects.all(),
        to_field_name="contact_id",
        label=_("Admin-C (contact_id)"),
    )
    admin_c_contact_id = django_filters.CharFilter(
        field_name="admin_c__contact_id",
        label=_("Admin-C (contact_id)"),
    )
    admin_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Admin-C (ID)"),
    )

    tech_c = django_filters.ModelMultipleChoiceFilter(
        field_name="tech_c__contact_id",
        queryset=RegistrationContact.objects.all(),
        to_field_name="contact_id",
        label=_("Tech-C (contact_id)"),
    )
    tech_c_contact_id = django_filters.CharFilter(
        field_name="tech_c__contact_id",
        label=_("Tech-C (contact_id)"),
    )
    tech_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Tech-C (ID)"),
    )

    billing_c = django_filters.ModelMultipleChoiceFilter(
        field_name="billing_c__contact_id",
        queryset=RegistrationContact.objects.all(),
        to_field_name="contact_id",
        label=_("Billing-C (contact_id)"),
    )
    billing_c_contact_id = django_filters.CharFilter(
        field_name="billing_c__contact_id",
        label=_("Billing-C (contact_id)"),
    )
    billing_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RegistrationContact.objects.all(),
        label=_("Billing-C (ID)"),
    )

    arpa_network = MultiValueCharFilter(
        method="filter_arpa_network",
        label=_("ARPA Network"),
    )
    active = django_filters.BooleanFilter(
        label=_("Zone is active"),
    )
    inline_signing = django_filters.BooleanFilter(
        label=_("Zone is using a DNSSEC policy with inline signing"),
        method="filter_inline_signing",
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

    def filter_inline_signing(self, queryset, name, value):
        if value is None:
            return queryset

        if value:
            return queryset.filter(
                dnssec_policy__isnull=False, dnssec_policy__inline_signing=True
            )
        else:
            return queryset.filter(
                Q(
                    Q(dnssec_policy__isnull=True)
                    | Q(dnssec_policy__inline_signing=False)
                )
            )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(status__icontains=value)
            | Q(view__name__icontains=value)
            | Q(dnssec_policy__name__icontains=value)
            | Q(registrar__name__icontains=value)
            | Q(registry_domain_id__icontains=value)
            | Q(registrant__name__icontains=value)
            | Q(admin_c__name__icontains=value)
            | Q(tech_c__name__icontains=value)
            | Q(billing_c__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)
