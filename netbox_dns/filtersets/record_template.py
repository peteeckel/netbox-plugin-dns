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
            "name",
            "record_name",
            "value",
            "description",
            "ttl",
            "disable_ptr",
        )

    type = django_filters.MultipleChoiceFilter(
        choices=RecordTypeChoices,
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RecordStatusChoices,
    )
    zone_template = django_filters.ModelMultipleChoiceFilter(
        queryset=ZoneTemplate.objects.all(),
        field_name="zone_templates__name",
        to_field_name="name",
        label=_("Zone Template"),
    )
    zone_template_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ZoneTemplate.objects.all(),
        field_name="zone_templates",
        to_field_name="id",
        label=_("Zone Template ID"),
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
