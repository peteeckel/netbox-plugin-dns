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
    class Meta:
        model = DNSSECKeyTemplate

        fields = (
            "id",
            "lifetime",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    type = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateTypeChoices,
    )
    algorithm = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateAlgorithmChoices,
    )
    key_size = django_filters.MultipleChoiceFilter(
        choices=DNSSECKeyTemplateKeySizeChoices,
    )

    policy = django_filters.ModelMultipleChoiceFilter(
        field_name="policies__name",
        queryset=DNSSECPolicy.objects.all(),
        to_field_name="name",
        label=_("DNSSEC Policy (name)"),
    )
    policy_name = django_filters.CharFilter(
        field_name="policies__name",
        distinct=True,
        label=_("DNSSEC Policy (name)"),
    )
    policy_id = django_filters.ModelMultipleChoiceFilter(
        field_name="policies",
        queryset=DNSSECPolicy.objects.all(),
        label=_("DNSSEC Policy (ID)"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(Q(name__icontains=value) | Q(description__icontains=value))
        return queryset.filter(qs_filter)
