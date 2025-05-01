from dns.dnssectypes import Algorithm

from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet

from .utilities import initialize_choice_names

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
    "DNSSECKeyTemplateKeySizeChoices",
)


class DNSSECKeyTemplateTypeChoices(ChoiceSet):
    TYPE_CSK = "CSK"
    TYPE_KSK = "KSK"
    TYPE_ZSK = "ZSK"

    CHOICES = [
        (TYPE_CSK, _("CSK"), "purple"),
        (TYPE_KSK, _("KSK"), "blue"),
        (TYPE_ZSK, _("ZSK"), "green"),
    ]


class DNSSECKeyTemplateKeySizeChoices(ChoiceSet):
    SIZE_512 = 512
    SIZE_1024 = 1024
    SIZE_2048 = 2048
    SIZE_3072 = 3072
    SIZE_4096 = 4096

    CHOICES = [
        (SIZE_512, 512),
        (SIZE_1024, 1024),
        (SIZE_2048, 2048),
        (SIZE_3072, 3072),
        (SIZE_4096, 4096),
    ]

    @classmethod
    def as_enum(cls):
        return super().as_enum(prefix="SIZE")


@initialize_choice_names
class DNSSECKeyTemplateAlgorithmChoices(ChoiceSet):
    CHOICES = [
        (algorithm.name, f"{algorithm.name} ({algorithm.value})")
        for algorithm in sorted(Algorithm, key=lambda a: a.value)
        if algorithm.value < 252 and algorithm not in DEPRECATED_ALGORITHMS
    ]
