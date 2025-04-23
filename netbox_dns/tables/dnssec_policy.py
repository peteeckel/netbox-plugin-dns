import django_tables2 as tables
from django.utils.translation import gettext_lazy as _


from netbox.tables import (
    NetBoxTable,
    TagColumn,
    ChoiceFieldColumn,
    ActionsColumn,
)
from tenancy.tables import TenancyColumnsMixin

from netbox_dns.models import DNSSECPolicy


__all__ = (
    "DNSSECPolicyTable",
    "DNSSECPolicyDisplayTable",
)


class DNSSECPolicyTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = DNSSECPolicy

        fields = ("description",)

        default_columns = (
            "name",
            "description",
            "status",
            "use_nsec3",
            "tags",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    status = ChoiceFieldColumn(
        verbose_name=_("Status"),
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
        verbose_name=_("Signatures Validity"),
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
    create_cdnskey = tables.BooleanColumn(
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
    use_nsec3 = tables.BooleanColumn(
        verbose_name=_("Use NSEC3"),
    )
    nsec3_iterations = tables.Column(
        verbose_name=_("NSEC3 Iterations"),
    )
    nsec3_opt_out = tables.BooleanColumn(
        verbose_name=_("NSEC3 Opt Out"),
    )
    nsec3_salt_size = tables.Column(
        verbose_name=_("NSEC3 Salt Size"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:dnssecpolicy_list",
    )


class DNSSECPolicyDisplayTable(TenancyColumnsMixin, NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = DNSSECPolicy

        fields = ("description",)

        default_columns = (
            "name",
            "description",
            "status",
            "tags",
        )

    name = tables.Column(
        verbose_name=_("Name"),
        linkify=True,
    )
    status = ChoiceFieldColumn(
        verbose_name=_("Status"),
    )
    create_cdnskey = tables.BooleanColumn(
        verbose_name=_("Create CDNSKEY"),
    )
    use_nsec3 = tables.BooleanColumn(
        verbose_name=_("Use NSEC3"),
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:dnssecpolicy_list",
    )
    actions = ActionsColumn(actions="")
