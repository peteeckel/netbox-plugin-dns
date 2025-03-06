import django_tables2 as tables
from django.utils.translation import gettext_lazy as _


from netbox.tables import (
    NetBoxTable,
    TagColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import DNSSECPolicy


__all__ = ("DNSSECPolicyTable",)


class DNSSECPolicyTable(TenancyColumnsMixin, NetBoxTable):
    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    inline_signing = tables.Column(
        verbose_name=_("Inline Signing"),
    )
    dnskey_ttl = tables.Column(
        verbose_name=_("DNSKEY TTL"),
    )
    purge_keys = tables.Column(
        verbose_name=_("Purge Keys"),
    )
    publish_safety = tables.Column(
        verbose_name=_("Publish Safety"),
    )
    retire_safety = tables.Column(
        verbose_name=_("Retire Safety"),
    )
    signatures_jitter = tables.Column(
        verbose_name=_("Signatures Jitter"),
    )
    signatures_refresh = tables.Column(
        verbose_name=_("Signatures Refresh"),
    )
    signatures_validity = tables.Column(
        verbose_name=_("Signatures Validitiy"),
    )
    signatures_validity_dnskey = tables.Column(
        verbose_name=_("Signatures Validity (DNSKEY)"),
    )
    max_zone_ttl = tables.Column(
        verbose_name=_("Max Zone TTL"),
    )
    dnskey_ttl = tables.Column(
        verbose_name=_("DNSKEY TTL"),
    )
    zone_propagation_delay = tables.Column(
        verbose_name=_("Zone Propagation Delay"),
    )
    create_cdnskey = tables.Column(
        verbose_name=_("Create CDNSKEY"),
    )
    cds_digest_types = tables.Column(
        verbose_name=_("CDS Digest Types"),
    )
    parent_ds_ttl = tables.Column(
        verbose_name=_("Parent DS TTL"),
    )
    parent_propagation_delay = tables.Column(
        verbose_name=_("Parent Propagation Delay"),
    )
    use_nsec3 = tables.Column(
        verbose_name=_("Use NSEC3"),
    )
    nsec3_iterations = tables.Column(
        verbose_name=_("NSEC3 Iterations"),
    )
    nsec3_opt_out = tables.Column(
        verbose_name=_("NSEC3 Opt Out"),
    )
    nsec3_salt_size = tables.Column(
        verbose_name=_("NSEC3 Salt Size"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:dnssecpolicy_list",
    )

    class Meta(NetBoxTable.Meta):
        model = DNSSECPolicy
        fields = ("description",)
        default_columns = (
            "name",
            "inline_signing",
            "use_nsec3",
            "tags",
        )
