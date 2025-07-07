from django.test import TestCase
from django.core import management

from netbox_dns.models import Zone, Record, NameServer
from netbox_dns.choices import RecordTypeChoices


class NetBoxDNSManagementCleanupRRsetTTLTestCase(TestCase):
    def test_cleanup_rrset_min_ttl(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        record1 = Record.objects.create(
            name="name1",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="name1",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::2",
            ttl=86400,
        )

        # +
        # Set different TTL on the second record of the RRset and its PTR record
        # (need to skip validation for this to work)
        # -
        record2.ttl = 43200
        super(Record, record2).save()
        record2.ptr_record.ttl = 43200
        super(Record, record2.ptr_record).save()

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record1.ptr_record.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)
        self.assertEqual(record2.ptr_record.ttl, 43200)

        management.call_command("cleanup_rrset_ttl", verbosity=0, min=True)

        record1.refresh_from_db()
        record2.refresh_from_db()

        self.assertEqual(record1.ttl, 43200)
        self.assertEqual(record1.ptr_record.ttl, 43200)
        self.assertEqual(record2.ttl, 43200)
        self.assertEqual(record2.ptr_record.ttl, 43200)

    def test_cleanup_rrset_max_ttl(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        record1 = Record.objects.create(
            name="name1",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::1",
            ttl=86400,
        )
        record2 = Record.objects.create(
            name="name1",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::2",
            ttl=86400,
        )

        # +
        # Set different TTL on the second record of the RRset and its PTR record
        # (need to skip validation for this to work)
        # -
        record2.ttl = 43200
        super(Record, record2).save()
        record2.ptr_record.ttl = 43200
        super(Record, record2.ptr_record).save()

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record1.ptr_record.ttl, 86400)
        self.assertEqual(record2.ttl, 43200)
        self.assertEqual(record2.ptr_record.ttl, 43200)

        management.call_command("cleanup_rrset_ttl", verbosity=0, max=True)

        record1.refresh_from_db()
        record2.refresh_from_db()

        self.assertEqual(record1.ttl, 86400)
        self.assertEqual(record1.ptr_record.ttl, 86400)
        self.assertEqual(record2.ttl, 86400)
        self.assertEqual(record2.ptr_record.ttl, 86400)
