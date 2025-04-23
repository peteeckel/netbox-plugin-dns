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
            "name",
            "default_view",
            "description",
        )

    prefix_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="prefixes",
        to_field_name="id",
        label=_("Prefix ID"),
    )
    prefix = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="prefixes__prefix",
        to_field_name="prefix",
        label=_("Prefix"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
