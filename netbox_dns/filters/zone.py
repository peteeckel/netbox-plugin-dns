import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import View, Zone, ZoneStatusChoices


class ZoneFilter(TenancyFilterSet, NetBoxModelFilterSet):
    status = django_filters.ChoiceFilter(
        choices=ZoneStatusChoices,
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        label="View ID",
    )
    view = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="view__name",
        to_field_name="name",
        label="View",
    )
    active = django_filters.BooleanFilter(
        label="Zone is active",
    )

    class Meta:
        model = Zone
        fields = ("id", "name", "view", "status", "nameservers", "active", "tenant")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(status__icontains=value)
            | Q(view__name__icontains=value)
        )
        return queryset.filter(qs_filter)
