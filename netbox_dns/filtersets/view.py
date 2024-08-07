from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import View


__all__ = ("ViewFilterSet",)


class ViewFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    class Meta:
        model = View
        fields = ("id", "name", "default_view", "description")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
