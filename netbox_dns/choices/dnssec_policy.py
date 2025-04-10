from dns.dnssectypes import DSDigest

from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet

from .utilities import initialize_choice_names

DEPRECATED_DIGESTS = (
    DSDigest.NULL,
    DSDigest.SHA1,
    DSDigest.GOST,
)


__all__ = (
    "DNSSECPolicyDigestChoices",
    "DNSSECPolicyStatusChoices",
)


@initialize_choice_names
class DNSSECPolicyDigestChoices(ChoiceSet):
    CHOICES = [
        (digest.name, digest.name)
        for digest in sorted(DSDigest, key=lambda a: a.name)
        if digest not in DEPRECATED_DIGESTS
    ]


class DNSSECPolicyStatusChoices(ChoiceSet):
    key = "DNSSECPolicy.status"

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    CHOICES = [
        (STATUS_ACTIVE, _("Active"), "blue"),
        (STATUS_INACTIVE, _("Inactive"), "red"),
    ]
