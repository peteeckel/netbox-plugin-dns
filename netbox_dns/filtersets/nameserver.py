import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import NameServer, Zone


class NameServerFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        to_field_name="id",
        label="Zones",
    )
    soa_zone_id = django_filters.ModelMultipleChoiceFilter(
        method="filter_soa_zones",
        queryset=Zone.objects.all(),
        label="SOA Zones",
    )

    class Meta:
        model = NameServer
        fields = ("id", "name", "description")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)

    def filter_soa_zones(self, queryset, name, value):
        if not value:
            return queryset
        soa_mnames = {zone.soa_mname.pk for zone in value}
        return queryset.filter(pk__in=soa_mnames)
