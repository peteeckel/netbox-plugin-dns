import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import DNSSECKeyTemplate, DNSSECPolicy
from netbox_dns.choices import (
    DNSSECKeyTemplateTypeChoices,
    DNSSECKeyTemplateAlgorithmChoices,
    DNSSECKeyTemplateKeySizeChoices,
)


__all__ = ("DNSSECKeyTemplateFilterSet",)


class DNSSECKeyTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateTypeChoices,
    )
    algorithm = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateAlgorithmChoices,
    )
    key_size = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateKeySizeChoices,
    )

    policies_id = django_filters.ModelMultipleChoiceFilter(
        field_name="policies",
        queryset=DNSSECPolicy.objects.all(),
        to_field_name="id",
        label=_("DNSSEC Policy IDs"),
    )
    policies = django_filters.ModelMultipleChoiceFilter(
        field_name="policies__name",
        queryset=DNSSECPolicy.objects.all(),
        to_field_name="name",
        label=_("DNSSEC Policies"),
    )

    class Meta:
        model = DNSSECKeyTemplate
        fields = ("id", "name", "description", "lifetime")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
