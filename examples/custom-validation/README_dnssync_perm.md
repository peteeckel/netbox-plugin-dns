# Custom validation of DNS permissions in DNSSYNC

## Purpose

By design, the NetBox DNS DNSsync feature does not check DNS permissions
when syncing DNS records through an action done in the IPAM.

The script *dnssync_perm.py* provides partial permission validation for
DNSsync, but only when adding or modification of IP address.

No permission is checked when deleting an IP address This is consistent
with the idea that IPAM actions have complete control over the DNSsync-ed
records.

## Installation

Copy this script to a "validators" directory into Netbox:

    mkdir -p /opt/netbox/netbox/validators
    cp dnssync_perm.py /opt/netbox/netbox/validators/

Activate the validator by adding the following lines in
/opt/netbox/netbox/netbox/configuration.py:

    from validators.dnssync_perm import NamePermissionValidator

    CUSTOM_VALIDATORS = {
         (NamePermissionValidator() ),
    }
