from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import DNSSECKeyTemplate


__all__ = ("DNSSECKeyTemplateFilterSet",)


class DNSSECKeyTemplateFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = DNSSECKeyTemplate
        fields = ("id", "name", "description")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
