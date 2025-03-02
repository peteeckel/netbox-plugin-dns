from dns.dnssectypes import DSDigest

from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet

from .utilities import define_choice_attributes

DEPRECATED_DIGESTS = (
    DSDigest.NULL,
    DSDigest.SHA1,
    DSDigest.GOST,
)


__all__ = (
    "DNSSECPolicyDigestChoices",
)


@define_choice_attributes()
class DNSSECPolicyDigestChoices(ChoiceSet):
    CHOICES = [
        (digest.name, digest.name)
        for digest in sorted(DSDigest, key=lambda a: a.name)
        if digest not in DEPRECATED_DIGESTS
    ]
