from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import Contact


class ContactFilter(NetBoxModelFilterSet):
    class Meta:
        model = Contact
        fields = (
            "id",
            "name",
            "contact_id",
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

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(contact_id__icontains=value)
            | Q(organization__icontains=value)
            | Q(city__icontains=value)
            | Q(state_province__icontains=value)
            | Q(street__icontains=value)
            | Q(country=value)
        )

        return queryset.filter(qs_filter)
