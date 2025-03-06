from dns.dnssectypes import Algorithm

from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet

from .utilities import define_choice_attributes

DEPRECATED_ALGORITHMS = (
    Algorithm.RSAMD5,
    Algorithm.DH,
    Algorithm.DSA,
    Algorithm.ECC,
    Algorithm.RSASHA1,
    Algorithm.DSANSEC3SHA1,
    Algorithm.RSASHA1NSEC3SHA1,
    Algorithm.RSASHA512,
    Algorithm.ECCGOST,
)


__all__ = (
    "DNSSECKeyTemplateTypeChoices",
    "DNSSECKeyTemplateAlgorithmChoices",
)


class DNSSECKeyTemplateTypeChoices(ChoiceSet):
    TYPE_CSK = "csk"
    TYPE_KSK = "ksk"
    TYPE_ZSK = "zsk"

    CHOICES = [
        (TYPE_CSK, _("CSK"), "purple"),
        (TYPE_KSK, _("KSK"), "blue"),
        (TYPE_ZSK, _("ZSK"), "green"),
    ]


@define_choice_attributes()
class DNSSECKeyTemplateAlgorithmChoices(ChoiceSet):
    CHOICES = [
        (algorithm.name, algorithm.name)
        for algorithm in sorted(Algorithm, key=lambda a: a.name)
        if algorithm.value < 252 and algorithm not in DEPRECATED_ALGORITHMS
    ]
