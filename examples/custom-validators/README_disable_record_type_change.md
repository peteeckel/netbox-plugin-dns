# Custom validator to disable changing the type of a DNS record

## Purpose

In [NetBox DNS issue #677](https://github.com/peteeckel/netbox-plugin-dns/issues/677),
it was suggested to disallow changing the record type. This custom validator adds the
desired functionality without making changes to the code base.

## Installation

Create a `validators` directory under the NetBox application path and copy this
validator script into it:

```
mkdir /opt/netbox/netbox/validators
cp disable_record_type_change.py /opt/netbox/netbox/validators/
```

Activate the validator by adding the following lines in `/opt/netbox/netbox/netbox/configuration.py`:

```
from validators.disable_record_type_change import TypeChangeValidator

CUSTOM_VALIDATORS = {
    "netbox_dns.record": (
        TypeChangeValidator(),
    ),
}
```

After making this change, restart NetBox to activate the new validator.
