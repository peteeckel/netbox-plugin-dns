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
            "name",
            "description",
            "status",
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
        label=_("DNSSEC Key Templates"),
    )
    key_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="key_templates",
        queryset=DNSSECKeyTemplate.objects.all(),
        to_field_name="id",
        label=_("DNSSEC Key Template IDs"),
    )
    zone = django_filters.ModelMultipleChoiceFilter(
        field_name="zones__name",
        queryset=Zone.objects.all(),
        to_field_name="name",
        label=_("Zones"),
    )
    zone_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zones",
        queryset=Zone.objects.all(),
        to_field_name="id",
        label=_("Zone IDs"),
    )
    zone_template = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates__name",
        queryset=ZoneTemplate.objects.all(),
        to_field_name="name",
        label=_("Zone Templates"),
    )
    zone_template_id = django_filters.ModelMultipleChoiceFilter(
        field_name="zone_templates",
        queryset=ZoneTemplate.objects.all(),
        to_field_name="id",
        label=_("Zone Template IDs"),
    )

    def filter_cds_digest_types(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(cds_digest_types__overlap=value)

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
