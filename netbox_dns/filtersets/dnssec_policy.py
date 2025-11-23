import django_filters

from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from netbox_dns.models import DNSSECPolicy, DNSSECKeyTemplate, Zone, ZoneTemplate
from netbox_dns.choices import DNSSECPolicyStatusChoices


__all__ = ("DNSSECPolicyFilterSet",)


class DNSSECPolicyFilterSet(TenancyFilterSet, NetBoxModelFilterSet):
    class Meta:
        model = DNSSECPolicy

        fields = (
            "id",
            "status",
            "inline_signing",
            "dnskey_ttl",
            "purge_keys",
            "publish_safety",
            "retire_safety",
            "signatures_jitter",
            "signatures_refresh",
            "signatures_validity",
            "signatures_validity_dnskey",
            "max_zone_ttl",
            "zone_propagation_delay",
            "create_cdnskey",
            "parent_ds_ttl",
            "parent_propagation_delay",
            "use_nsec3",
            "nsec3_iterations",
            "nsec3_opt_out",
            "nsec3_salt_size",
        )

    name = django_filters.CharFilter(
        label=_("Name"),
    )
    description = django_filters.CharFilter(
        label=_("Description"),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DNSSECPolicyStatusChoices,
    )
    cds_digest_types = MultiValueCharFilter(
        method="filter_cds_digest_types",
        label=_("CDS Digest Types"),
    )

    key_template = django_filters.ModelMultipleChoiceFilter(
        field_name="key_templates__name",
        queryset=DNSSECKeyTemplate.objects.all(),
        to_field_name="name",
        label=_("DNSSEC Key Template (name)"),
    )
    key_template_name = django_filters.CharFilter(
        field_name="key_templates__name",
        distinct=True,
        label=_("DNSSEC Key Template (name)"),
    )
    key_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="key_templates",
        queryset=DNSSECKeyTemplate.objects.all(),
        label=_("DNSSEC Key Template (ID)"),
    )

    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zone (name)"),
    )
    zone_name = django_filters.CharFilter(
        field_name="zones__name",
        distinct=True,
        label=_("Zone (name)"),
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        label=_("Zone (ID)"),
    )

    zone_template = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates__name",
        queryset=ZoneTemplate.objects.all(),
        to_field_name="name",
        label=_("Zone Template (name)"),
    )
    zone_template_name = django_filters.CharFilter(
        field_name="zone_templates__name",
        distinct=True,
        label=_("Zone Template (name)"),
    )
    zone_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates",
        queryset=ZoneTemplate.objects.all(),
        label=_("Zone Template (ID)"),
    )

    def filter_cds_digest_types(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(cds_digest_types__overlap=value)

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(Q(name__icontains=value) | Q(description__icontains=value))
        return queryset.filter(qs_filter)
