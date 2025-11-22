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
            "disable_ptr",
            "managed",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    fqdn = django_filters.CharFilter(
        label=_("FQDN"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    ttl = django_filters.CharFilter(
        label=_("TTL"),
    )
    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RecordStatusChoices,
    )

    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zone__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    zone_name = django_filters.CharFilter(
        field_name="zone__name",
        label=_("Zone Name"),
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    view = django_filters.ModelMultipleChoiceFilter(
        field_name="zone__view__name",
        queryset=View.objects.all(),
        to_field_name="name",
        label=_("View"),
    )
    view_name = django_filters.CharFilter(
        field_name="zone__view__name",
        label=_("View Name"),
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zone__view",
        queryset=View.objects.all(),
        label=_("View ID"),
    )

    value = django_filters.CharFilter(
        label=_("Value"),
    )

    address_record_id = django_filters.ModelMultipleChoiceFilter(
        field_name="address_records",
        queryset=Record.objects.all(),
        label=_("Address Records"),
    )
    ptr_record_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Record.objects.all(),
        label=_("Pointer Record"),
    )
    rfc2317_cname_record_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Record.objects.all(),
        label=_("Pointer Record"),
    )
    ipam_ip_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
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
            | Q(description__icontains=value)
            | Q(value__icontains=value)
            | Q(zone__name__icontains=value)
        )
        return queryset.filter(qs_filter)
