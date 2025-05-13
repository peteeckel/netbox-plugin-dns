import netaddr

import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from ipam.models import IPAddress

from netbox_dns.models import View, Zone, Record
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


__all__ = ("RecordFilterSet",)


class RecordFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = Record

        fields = (
            "id",
            "name",
            "fqdn",
            "description",
            "ttl",
            "value",
            "disable_ptr",
            "managed",
        )

    fqdn = MultiValueCharFilter(
        method="filter_fqdn",
    )
    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RecordStatusChoices,
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        label=_("Parent Zone ID"),
    )
    zone = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        field_name="zone__name",
        to_field_name="name",
        label=_("Parent Zone"),
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="zone__view",
        label=_("ID of the View the Parent Zone belongs to"),
    )
    view = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="zone__view__name",
        to_field_name="name",
        label=_("View the Parent Zone belongs to"),
    )
    address_record_id = django_filters.ModelMultipleChoiceFilter(
        field_name="address_records",
        queryset=Record.objects.all(),
        to_field_name="id",
        label=_("Address Records"),
    )
    ptr_record_id = django_filters.ModelMultipleChoiceFilter(
        field_name="ptr_record",
        queryset=Record.objects.all(),
        to_field_name="id",
        label=_("Pointer Record"),
    )
    rfc2317_cname_record_id = django_filters.ModelMultipleChoiceFilter(
        field_name="rfc2317_cname_record",
        queryset=Record.objects.all(),
        to_field_name="id",
        label=_("Pointer Record"),
    )
    ipam_ip_address_id = django_filters.ModelMultipleChoiceFilter(
        field_name="ipam_ip_address",
        queryset=IPAddress.objects.all(),
        to_field_name="id",
        label=_("IPAM IP Address"),
    )
    ip_address = MultiValueCharFilter(
        method="filter_ip_address",
        label=_("IP Address"),
    )
    active = django_filters.BooleanFilter(
        label=_("Record is active"),
    )

    managed = django_filters.BooleanFilter()

    def filter_fqdn(self, queryset, name, value):
        if not value:
            return queryset

        fqdns = []
        for fqdn in value:
            if not fqdn.endswith("."):
                fqdn = fqdn + "."
            fqdns.append(fqdn)

        return queryset.filter(fqdn__in=fqdns)

    def filter_ip_address(self, queryset, name, value):
        if not value:
            return queryset
        try:
            ip_addresses = [
                str(netaddr.IPAddress(item)) for item in value if item.strip()
            ]
            if not ip_addresses:
                return queryset

            return queryset.filter(ip_address__in=ip_addresses)
        except (netaddr.AddrFormatError, ValueError):
            return queryset.none()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(fqdn__icontains=value)
            | Q(value__icontains=value)
            | Q(zone__name__icontains=value)
        )
        return queryset.filter(qs_filter)
