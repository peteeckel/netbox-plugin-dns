import dns
from dns import rdata, name as dns_name

from django.core.exceptions import ValidationError

from netbox_dns.choices import RecordClassChoices, RecordTypeChoices
from netbox_dns.validators import (
    validate_fqdn,
    validate_domain_name,
    validate_generic_name,
)


__all__ = ("validate_record_value",)


def validate_record_value(record_type, value):
    def _validate_idn(name):
        try:
            name.to_unicode()
        except dns_name.IDNAException as exc:
            raise ValidationError(
                f"{name.to_text()} is not a valid IDN: {exc}."
            ) from None

    try:
        rr = rdata.from_text(RecordClassChoices.IN, record_type, value)
    except dns.exception.SyntaxError as exc:
        raise ValidationError(
            f"Record value {value} is not a valid value for a {record_type} record: {exc}."
        ) from None

    match record_type:
        case RecordTypeChoices.CNAME:
            _validate_idn(rr.target)
            validate_domain_name(
                rr.target.to_text(),
                always_tolerant=True,
                allow_empty_label=True,
            )

        case (
            RecordTypeChoices.NS
            | RecordTypeChoices.HTTPS
            | RecordTypeChoices.SRV
            | RecordTypeChoices.SVCB
        ):
            _validate_idn(rr.target)
            validate_domain_name(rr.target.to_text(), always_tolerant=True)

        case RecordTypeChoices.DNAME:
            _validate_idn(rr.target)
            validate_domain_name(
                rr.target.to_text(), always_tolerant=True, zone_name=True
            )

        case RecordTypeChoices.PTR | RecordTypeChoices.NSAP_PTR:
            _validate_idn(rr.target)
            validate_fqdn(rr.target.to_text(), always_tolerant=True)

        case RecordTypeChoices.MX | RecordTypeChoices.RT | RecordTypeChoices.KX:
            _validate_idn(rr.exchange)
            validate_domain_name(rr.exchange.to_text(), always_tolerant=True)

        case RecordTypeChoices.NSEC:
            _validate_idn(rr.next)
            validate_domain_name(rr.next.to_text(), always_tolerant=True)

        case RecordTypeChoices.RP:
            _validate_idn(rr.mbox)
            validate_domain_name(rr.mbox.to_text(), always_tolerant=True)
            _validate_idn(rr.txt)
            validate_domain_name(rr.txt.to_text(), always_tolerant=True)

        case RecordTypeChoices.NAPTR:
            _validate_idn(rr.replacement)
            validate_generic_name(rr.replacement.to_text(), always_tolerant=True)

        case RecordTypeChoices.PX:
            _validate_idn(rr.map822)
            validate_domain_name(rr.map822.to_text(), always_tolerant=True)
            _validate_idn(rr.mapx400)
            validate_domain_name(rr.mapx400.to_text(), always_tolerant=True)
