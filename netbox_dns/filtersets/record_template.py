import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import RecordTemplate, ZoneTemplate
from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


__all__ = ("RecordTemplateFilterSet",)


class RecordTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = RecordTemplate

        fields = (
            "id",
            "disable_ptr",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    record_name = django_filters.CharFilter(
        label=_("Record Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    ttl = django_filters.CharFilter(
        label=_("TTL"),
    )
    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
        label=_("Type"),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RecordStatusChoices,
        label=_("Status"),
    )
    value = django_filters.CharFilter(
        label=_("Value"),
    )

    zone_template = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates__name",
        queryset=ZoneTemplate.objects.all(),
        to_field_name="name",
        label=_("Zone Template"),
    )
    zone_template_name = django_filters.CharFilter(
        field_name="zone_templates__name",
        distinct=True,
        label=_("Zone Template"),
    )
    zone_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates",
        queryset=ZoneTemplate.objects.all(),
        label=_("Zone Template ID"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(record_name__icontains=value)
            | Q(value__icontains=value)
        )
        return queryset.filter(qs_filter)
