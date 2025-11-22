import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import Registrar, Zone


__all__ = ("RegistrarFilterSet",)


class RegistrarFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Registrar

        fields = (
            "id",
            "iana_id",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )

    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    zone_name = django_filters.CharFilter(
        field_name="zones__name",
        distinct=True,
        label=_("Zone Name"),
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(iana_id=value)
            | Q(referral_url__icontains=value)
            | Q(whois_server__icontains=value)
            | Q(address__icontains=value)
            | Q(abuse_email__icontains=value)
            | Q(abuse_phone__icontains=value)
        )

        return queryset.filter(qs_filter)
