import django_filters

from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from ipam.models import Prefix

from netbox_dns.models import View


__all__ = ("ViewFilterSet",)


class ViewFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    class Meta:
        model = View

        fields = (
            "id",
            "default_view",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    prefix = django_filters.ModelMultipleChoiceFilter(
        field_name="prefixes__prefix",
        queryset=Prefix.objects.all(),
        to_field_name="prefix",
        label=_("Prefix"),
    )
    prefix_prefix = django_filters.CharFilter(
        field_name="prefixes__prefix",
        distinct=True,
        label=_("Prefix"),
    )
    prefix_id = django_filters.ModelMultipleChoiceFilter(
        field_name="prefixes",
        queryset=Prefix.objects.all(),
        label=_("Prefix ID"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(Q(name__icontains=value) | Q(description__icontains=value))

        return queryset.filter(qs_filter)
