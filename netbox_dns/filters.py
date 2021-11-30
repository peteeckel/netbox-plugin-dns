import django_filters
from django.db.models import Q

from extras.filters import TagFilter
from netbox.filtersets import PrimaryModelFilterSet
from .models import NameServer, Record, Zone


class ZoneFilter(PrimaryModelFilterSet):
    """Filter capabilities for Zone instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    name = django_filters.CharFilter(
        lookup_expr="icontains",
    )
    status = django_filters.ChoiceFilter(
        choices=Zone.CHOICES,
    )
    tag = TagFilter()

    class Meta:
        model = Zone
        fields = ("name", "status", "nameservers", "tag")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(status__icontains=value)
        return queryset.filter(qs_filter)


class NameServerFilter(PrimaryModelFilterSet):
    """Filter capabilities for NameServer instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    name = django_filters.CharFilter(
        lookup_expr="icontains",
    )
    tag = TagFilter()

    class Meta:
        model = NameServer
        fields = ("name", "tag")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)


class RecordFilter(PrimaryModelFilterSet):
    """Filter capabilities for Record instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    type = django_filters.MultipleChoiceFilter(
        choices=Record.CHOICES,
        null_value=None,
    )
    name = django_filters.CharFilter(
        lookup_expr="icontains",
    )
    value = django_filters.CharFilter(
        lookup_expr="icontains",
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        label="Parent Zone ID",
    )
    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zone__name",
        to_field_name="name",
        queryset=Zone.objects.all(),
        label="Parent Zone",
    )
    tag = TagFilter()
    managed = django_filters.BooleanFilter()

    class Meta:
        model = Record
        fields = ("type", "name", "value", "tag", "managed")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
