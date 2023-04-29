import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import View


class ViewFilter(NetBoxModelFilterSet):
    """Filter capabilities for View instances."""

    name = django_filters.CharFilter()

    class Meta:
        model = View
        fields = ("id", "name")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
