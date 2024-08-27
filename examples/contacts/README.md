# Assigning Contacts to Records and Zones.

You must have already created:

- The actual contact you wish to assign to the record/zone.
- a contact role.  It's suggested that roles are different for records vs. zones.
- The dns record/zone already exists.

The ansible playbook `assign-contacts.yaml` contains a sample task to update netbox using the URI mechanism.
It uses the netbox `query` plugin to determine the correct rest call.

## To see the assignments.

Visit either contact assigned, or use the Contact Assignments search page.

## Web interface

At this time, there is no web interface to add contacts on the Records or Zones pages.

