import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import DNSSECKey, DNSSECPolicy


__all__ = ("DNSSECKeyFilterSet",)


class DNSSECKeyFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    policy_id = django_filters.ModelMultipleChoiceFilter(
        field_name="policies",
        queryset=DNSSECPolicy.objects.all(),
        to_field_name="id",
        label=_("Policies"),
    )

    class Meta:
        model = DNSSECKey
        fields = ("id", "name", "description")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
