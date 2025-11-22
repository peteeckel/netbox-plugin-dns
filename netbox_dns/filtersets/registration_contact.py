import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import RegistrationContact, Zone


__all__ = ("RegistrationContactFilterSet",)


class RegistrationContactFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = RegistrationContact

        fields = (
            "id",
            "organization",
            "street",
            "city",
            "state_province",
            "postal_code",
            "country",
            "phone",
            "phone_ext",
            "fax",
            "fax_ext",
            "email",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    contact_id = django_filters.CharFilter(
        label=_("Contact ID"),
    )

    admin_c_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="admin_c_zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    admin_c_zone_name = django_filters.CharFilter(
        field_name="admin_c_zones__name",
        distinct=True,
        label=_("Zone Name"),
    )
    admin_c_zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="admin_c_zones",
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    billing_c_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="billing_c_zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    billing_c_zone_name = django_filters.CharFilter(
        field_name="billing_c_zones__name",
        distinct=True,
        label=_("Zone Name"),
    )
    billing_c_zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="billing_c_zones",
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    tech_c_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="tech_c_zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    tech_c_zone_name = django_filters.CharFilter(
        field_name="tech_c_zones__name",
        distinct=True,
        label=_("Zone Name"),
    )
    tech_c_zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="tech_c_zones",
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    registrant_zone = django_filters.ModelMultipleChoiceFilter(
        field_name="registrant_zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone"),
    )
    registrant_zone_name = django_filters.CharFilter(
        field_name="registrant_zones__name",
        distinct=True,
        label=_("Zone Name"),
    )
    registrant_zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="registrant_zones",
        queryset=Zone.objects.all(),
        label=_("Zone ID"),
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(contact_id__icontains=value)
            | Q(organization__icontains=value)
            | Q(city__icontains=value)
            | Q(state_province__icontains=value)
            | Q(street__icontains=value)
            | Q(country=value)
        )

        return queryset.filter(qs_filter)
