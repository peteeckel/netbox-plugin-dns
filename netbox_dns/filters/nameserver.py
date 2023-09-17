import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import NameServer


class NameServerFilter(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = NameServer
        fields = ("id", "name", "tenant")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
