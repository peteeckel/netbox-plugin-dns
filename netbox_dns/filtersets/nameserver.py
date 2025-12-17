import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filtersets import register_filterset

from netbox_dns.models import NameServer, Zone


__all__ = ("NameServerFilterSet",)


@register_filterset
class NameServerFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = NameServer

        fields = (
            "id",
            "name",
            "description",
        )

    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        label=_("Zone (ID)"),
    )
    soa_zone_id = django_filters.ModelMultipleChoiceFilter(
        method="filter_soa_zones",
        queryset=Zone.objects.all(),
        label=_("SOA Zone (ID)"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(Q(name__icontains=value) | Q(description__icontains=value))
        return queryset.filter(qs_filter)

    def filter_soa_zones(self, queryset, name, value):
        if not value:
            return queryset
        soa_mnames = {zone.soa_mname.pk for zone in value}
        return queryset.filter(pk__in=soa_mnames)
