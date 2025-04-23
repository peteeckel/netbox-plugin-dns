from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_dns.models import Registrar


__all__ = ("RegistrarFilterSet",)


class RegistrarFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Registrar

        fields = (
            "id",
            "name",
            "description",
            "iana_id",
            "address",
            "referral_url",
            "whois_server",
            "abuse_email",
            "abuse_phone",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(iana_id=value)
            | Q(referral_url__icontains=value)
            | Q(whois_server__icontains=value)
            | Q(address__icontains=value)
            | Q(abuse_email__icontains=value)
            | Q(abuse_phone__icontains=value)
        )

        return queryset.filter(qs_filter)
