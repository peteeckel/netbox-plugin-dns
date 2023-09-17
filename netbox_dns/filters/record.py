import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import View, Zone, Record, RecordTypeChoices


class RecordFilter(TenancyFilterSet, NetBoxModelFilterSet):
    """Filter capabilities for Record instances."""

    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
        null_value=None,
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        label="Parent Zone ID",
    )
    zone = django_filters.ModelMultipleChoiceFilter(
        queryset=Zone.objects.all(),
        field_name="zone__name",
        to_field_name="name",
        label="Parent Zone",
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="zone__view",
        label="ID of the View the Parent Zone belongs to",
    )
    view = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="zone__view__name",
        to_field_name="name",
        label="View the Parent Zone belongs to",
    )
    managed = django_filters.BooleanFilter()

    class Meta:
        model = Record
        fields = ("id", "type", "name", "value", "status", "zone", "managed", "tenant")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(value__icontains=value)
            | Q(zone__name__icontains=value)
        )
        return queryset.filter(qs_filter)
