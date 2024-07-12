import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import RecordTemplate
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


__ALL__ = ("RecordTemplateFilterSet",)


class RecordTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RecordStatusChoices,
    )

    class Meta:
        model = RecordTemplate
        fields = (
            "id",
            "name",
            "record_name",
            "value",
            "status",
            "description",
            "ttl",
            "disable_ptr",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(record_name__icontains=value)
            | Q(value__icontains=value)
        )
        return queryset.filter(qs_filter)
