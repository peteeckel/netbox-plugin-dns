import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet

from netbox_dns.models import View, Zone, ZoneStatusChoices, Registrar, Contact


class ZoneFilter(TenancyFilterSet, NetBoxModelFilterSet):
    status = django_filters.ChoiceFilter(
        choices=ZoneStatusChoices,
    )
    view_id = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        label="View ID",
    )
    view = django_filters.ModelMultipleChoiceFilter(
        queryset=View.objects.all(),
        field_name="view__name",
        to_field_name="name",
        label="View",
    )
    registrar_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        label="Registrar ID",
    )
    registrar = django_filters.ModelMultipleChoiceFilter(
        queryset=Registrar.objects.all(),
        field_name="registrar__name",
        to_field_name="name",
        label="Registrar",
    )
    registrant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Registrant ID",
    )
    registrant = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="registrant__contact_id",
        to_field_name="contact_id",
        label="Registrant",
    )
    admin_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Administrative Contact ID",
    )
    admin_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="admin_c__contact_id",
        to_field_name="contact_id",
        label="Administrative Contact",
    )
    tech_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Technical Contact ID",
    )
    tech_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="tech_c__contact_id",
        to_field_name="contact_id",
        label="Technical Contact",
    )
    billing_c_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label="Billing Contact ID",
    )
    billing_c = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name="billing_c__contact_id",
        to_field_name="contact_id",
        label="Billing Contact",
    )

    active = django_filters.BooleanFilter(
        label="Zone is active",
    )

    class Meta:
        model = Zone
        fields = (
            "id",
            "name",
            "view",
            "status",
            "nameservers",
            "registrar",
            "registry_domain_id",
            "registrant",
            "admin_c",
            "tech_c",
            "billing_c",
            "active",
            "tenant",
        )

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(status__icontains=value)
            | Q(view__name__icontains=value)
            | Q(registrar__name__icontains=value)
            | Q(registry_domain_id__icontains=value)
            | Q(registrant__name__icontains=value)
            | Q(admin_c__name__icontains=value)
            | Q(tech_c__name__icontains=value)
            | Q(billing_c__name__icontains=value)
        )
        return queryset.filter(qs_filter)
