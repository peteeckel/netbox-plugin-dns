import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import NameServer


class NameServerFilter(NetBoxModelFilterSet):
    """Filter capabilities for NameServer instances."""

    name = django_filters.CharFilter()

    class Meta:
        model = NameServer
        fields = ("id", "name")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
