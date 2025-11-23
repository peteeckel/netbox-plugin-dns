import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import NameServer, Zone


__all__ = ("NameServerFilterSet",)


class NameServerFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = NameServer

        fields = ("id",)

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )

    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone (name)"),
    )
    zone_name = django_filters.CharFilter(
        field_name="zones__name",
        distinct=True,
        label=_("Zone (name)"),
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        label=_("Zone (ID)"),
    )

    soa_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="soa_zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("SOA Zone (name)"),
    )
    soa_zone_name = django_filters.CharFilter(
        field_name="soa_zones__name",
        distinct=True,
        label=_("SOA Zone (name)"),
    )
    soa_zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="soa_zones",
        queryset=Zone.objects.all(),
        label=_("SOA Zone (ID)"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(Q(name__icontains=value) | Q(description__icontains=value))
        return queryset.filter(qs_filter)
