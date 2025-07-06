import netaddr
from netaddr import IPNetwork

from dns import rdata
from dns.rdtypes.ANY import SOA

from django.test import TestCase
from django.core import management
from django.conf import settings

from ipam.models import IPAddress, Prefix

from netbox_dns.models import Zone, Record, NameServer
from netbox_dns.choices import RecordClassChoices, RecordTypeChoices


def parse_soa_value(soa):
    return rdata.from_text(
        rdclass=RecordClassChoices.IN, rdtype=RecordTypeChoices.SOA, tok=soa
    )


class NetBoxDNSManagementCleanupDatabaseTestCase(TestCase):
    def test_cleanup_ns_records(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        test_settings["enforce_unique_records"] = False

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            nameserver1 = NameServer.objects.create(name="ns1.example.com")
            nameserver2 = NameServer.objects.create(name="ns2.example.com")

            zone = Zone.objects.create(
                name="zone1.example.com",
                soa_mname=nameserver1,
                soa_rname="hostmaster.example.com",
            )
            zone.nameservers.set([nameserver1, nameserver2])

            ns1_record = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver1.name}.",
            )
            ns2_record = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver2.name}.",
            )
            self.assertTrue(ns1_record.exists())
            self.assertTrue(ns2_record.exists())

            # +
            # Remove NS record for ns2.example.com
            # -
            ns2_record.delete()

            # +
            # Duplicate NS record for ns1.example.com
            # -
            Record.objects.create(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver1.name}.",
            )

            # +
            # NS record with no matching NS for ns3.example.com
            # -
            Record.objects.create(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value="ns3.example.com.",
            )

            # +
            # Remove the 'managed' flag from the NS record for ns1.example.com
            # -
            ns1_record.update(managed=False)

            management.call_command("cleanup_database", verbosity=0)

            ns1_record = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver1.name}.",
            )
            ns2_record = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value=f"{nameserver2.name}.",
            )
            ns3_record = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.NS,
                value="ns3.example.com.",
            )

            self.assertTrue(ns1_record.exists())
            self.assertEqual(ns1_record.count(), 1)
            self.assertTrue(ns1_record.first().managed)
            self.assertTrue(ns2_record.exists())
            self.assertFalse(ns3_record.exists())

    def test_cleanup_soa_records(self):
        test_settings = settings.PLUGINS_CONFIG["netbox_dns"].copy()
        test_settings["enforce_unique_records"] = False

        with self.settings(PLUGINS_CONFIG={"netbox_dns": test_settings}):
            nameserver = NameServer.objects.create(name="ns1.example.com")

            zone = Zone.objects.create(
                name="zone1.example.com",
                soa_mname=nameserver,
                soa_rname="hostmaster.example.com",
            )
            zone.nameservers.set([nameserver])

            soa_record = Record.objects.get(
                name="@",
                zone=zone,
                type=RecordTypeChoices.SOA,
            )
            soa_fields = parse_soa_value(soa_record.value)

            self.assertEqual(soa_fields.mname.to_text(), f"{nameserver.name}.")
            self.assertEqual(soa_fields.rname.to_text(), "hostmaster.example.com.")
            self.assertEqual(soa_fields.refresh, test_settings.get("zone_soa_refresh"))
            self.assertEqual(soa_fields.retry, test_settings.get("zone_soa_retry"))
            self.assertEqual(soa_fields.expire, test_settings.get("zone_soa_expire"))
            self.assertEqual(soa_fields.minimum, test_settings.get("zone_soa_minimum"))
            self.assertEqual(soa_record.ttl, test_settings.get("zone_soa_ttl"))

            # +
            # Mangle the existing SOA record with wrong values
            # -
            soa_record.mname = "ns3.example.com."
            soa_record.rname = "fake.hostmaster.example.com."
            soa_record.serial = 23
            soa_record.refresh = 23
            soa_record.retry = 23
            soa_record.expire = 23
            soa_record.minimum = 23
            soa_record.managed = False
            soa_record.save()

            # +
            # Obsolete duplicate SOA record (validation needs to be bypassed for this)
            # -
            soa_record2 = Record(
                name="@",
                zone=zone,
                type=RecordTypeChoices.SOA,
                ttl=42,
                value=SOA.SOA(
                    rdclass=RecordClassChoices.IN,
                    rdtype=RecordTypeChoices.SOA,
                    mname="ns2.example.com.",
                    rname="bogus.hostmaster.example.com.",
                    serial=42,
                    refresh=42,
                    retry=42,
                    expire=42,
                    minimum=42,
                ),
            )
            super(Record, soa_record2).save()

            management.call_command("cleanup_database", verbosity=0)

            soa_records = Record.objects.filter(
                name="@",
                zone=zone,
                type=RecordTypeChoices.SOA,
            )

            self.assertEqual(soa_records.count(), 1)

            soa_record = soa_records.first()
            self.assertEqual(soa_record.ttl, zone.soa_ttl)
            self.assertTrue(soa_record.managed)

            soa_fields = parse_soa_value(soa_record.value)
            self.assertEqual(soa_fields.mname.to_text(), f"{nameserver.name}.")
            self.assertEqual(soa_fields.rname.to_text(), "hostmaster.example.com.")
            self.assertEqual(soa_fields.refresh, test_settings.get("zone_soa_refresh"))
            self.assertEqual(soa_fields.retry, test_settings.get("zone_soa_retry"))
            self.assertEqual(soa_fields.expire, test_settings.get("zone_soa_expire"))
            self.assertEqual(soa_fields.minimum, test_settings.get("zone_soa_minimum"))
            self.assertEqual(soa_record.ttl, test_settings.get("zone_soa_ttl"))

    def test_update_arpa_network(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        ipv4_zone = Zone.objects.create(
            name="0.0.10.in-addr.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        ipv6_zone = Zone.objects.create(
            name="8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        self.assertEqual(ipv4_zone.arpa_network, IPNetwork("10.0.0.0/24"))
        self.assertEqual(ipv6_zone.arpa_network, IPNetwork("2001:db8::/32"))

        # +
        # Delete the ARPA network property from the zones (need to skip the
        # standard save() method for this to work)
        # -
        ipv4_zone.arpa_network = None
        super(Zone, ipv4_zone).save()
        ipv6_zone.arpa_network = None
        super(Zone, ipv6_zone).save()

        self.assertIsNone(ipv4_zone.arpa_network)
        self.assertIsNone(ipv6_zone.arpa_network)

        management.call_command("cleanup_database", verbosity=0)

        ipv4_zone.refresh_from_db()
        ipv6_zone.refresh_from_db()

        self.assertEqual(ipv4_zone.arpa_network, IPNetwork("10.0.0.0/24"))
        self.assertEqual(ipv6_zone.arpa_network, IPNetwork("2001:db8::/32"))

    def test_cleanup_disable_ptr(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        records = (
            Record(
                name="name1",
                zone=zone,
                type=RecordTypeChoices.A,
                value="10.0.0.1",
                disable_ptr=True,
            ),
            Record(
                name="name2",
                zone=zone,
                type=RecordTypeChoices.A,
                value="10.0.0.2",
                disable_ptr=False,
            ),
            Record(
                name="name3",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
                disable_ptr=True,
            ),
            Record(
                name="name4",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
                disable_ptr=False,
            ),
            Record(
                name="name5",
                zone=zone,
                type=RecordTypeChoices.TXT,
                value="v=dmarc1, p=reject",
                disable_ptr=True,
            ),
            Record(
                name="name6",
                zone=zone,
                type=RecordTypeChoices.CNAME,
                value="name1",
                disable_ptr=True,
            ),
        )
        for record in records:
            super(Record, record).save()

        self.assertTrue(records[0].disable_ptr)
        self.assertFalse(records[1].disable_ptr)
        self.assertTrue(records[2].disable_ptr)
        self.assertFalse(records[3].disable_ptr)
        self.assertTrue(records[4].disable_ptr)
        self.assertTrue(records[5].disable_ptr)

        management.call_command("cleanup_database", verbosity=0)

        for record in records:
            record.refresh_from_db()

        self.assertTrue(records[0].disable_ptr)
        self.assertFalse(records[1].disable_ptr)
        self.assertTrue(records[2].disable_ptr)
        self.assertFalse(records[3].disable_ptr)
        self.assertFalse(records[4].disable_ptr)
        self.assertFalse(records[5].disable_ptr)

    def test_update_ptr_record(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        f_zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.10.in-addr.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        records = (
            Record(
                name="name1", zone=f_zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ),
            Record(
                name="name2", zone=f_zone, type=RecordTypeChoices.A, value="10.0.0.2"
            ),
            Record(
                name="name3",
                zone=f_zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
            ),
            Record(
                name="name4",
                zone=f_zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::2",
            ),
        )
        for record in records:
            record.save()

        ptr_record0 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[0]]
        )
        ptr_record1 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[1]]
        )
        ptr_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[2]]
        )
        ptr_record3 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[3]]
        )

        self.assertEqual(ptr_record0.value, records[0].fqdn)
        self.assertEqual(ptr_record0.name, "1")
        self.assertEqual(ptr_record1.value, records[1].fqdn)
        self.assertEqual(ptr_record1.name, "2")
        self.assertEqual(ptr_record2.value, records[2].fqdn)
        self.assertEqual(ptr_record2.name, "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
        self.assertEqual(ptr_record3.value, records[3].fqdn)
        self.assertEqual(ptr_record3.name, "2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")

        ptr_record0.delete()
        ptr_record1.value = "invalid.value."
        ptr_record1.managed = False
        ptr_record1.save()
        ptr_record2.delete()
        ptr_record3.value = "invalid.value."
        ptr_record3.managed = False
        ptr_record3.save()

        management.call_command("cleanup_database", verbosity=0)

        ptr_record0 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[0]]
        )
        ptr_record1.refresh_from_db()
        ptr_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[2]]
        )
        ptr_record3.refresh_from_db()

        self.assertEqual(ptr_record0.value, records[0].fqdn)
        self.assertEqual(ptr_record0.name, "1")
        self.assertEqual(ptr_record1.value, records[1].fqdn)
        self.assertEqual(ptr_record1.name, "2")
        self.assertTrue(ptr_record1.managed)
        self.assertEqual(ptr_record2.value, records[2].fqdn)
        self.assertEqual(ptr_record2.name, "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
        self.assertEqual(ptr_record3.value, records[3].fqdn)
        self.assertEqual(ptr_record3.name, "2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
        self.assertTrue(ptr_record3.managed)

    def test_update_ip_address(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        f_zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.10.in-addr.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        Zone.objects.create(
            name="0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        records = (
            Record(
                name="name1", zone=f_zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ),
            Record(
                name="name2", zone=f_zone, type=RecordTypeChoices.A, value="10.0.0.2"
            ),
            Record(
                name="name3",
                zone=f_zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
            ),
            Record(
                name="name4",
                zone=f_zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::2",
            ),
        )
        for record in records:
            record.save()

        ptr_record0 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[0]]
        )
        ptr_record1 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[1]]
        )
        ptr_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[2]]
        )
        ptr_record3 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[3]]
        )

        self.assertEqual(records[0].ip_address, netaddr.IPAddress("10.0.0.1"))
        self.assertEqual(ptr_record0.ip_address, netaddr.IPAddress("10.0.0.1"))
        self.assertEqual(records[1].ip_address, netaddr.IPAddress("10.0.0.2"))
        self.assertEqual(ptr_record1.ip_address, netaddr.IPAddress("10.0.0.2"))
        self.assertEqual(records[2].ip_address, netaddr.IPAddress("2001:db8::1"))
        self.assertEqual(ptr_record2.ip_address, netaddr.IPAddress("2001:db8::1"))
        self.assertEqual(records[3].ip_address, netaddr.IPAddress("2001:db8::2"))
        self.assertEqual(ptr_record3.ip_address, netaddr.IPAddress("2001:db8::2"))

        records[0].ip_address = None
        super(Record, records[0]).save()
        records[1].ip_address = netaddr.IPAddress("10.0.0.3")
        super(Record, records[1]).save()
        records[2].ip_address = None
        super(Record, records[2]).save()
        records[3].ip_address = netaddr.IPAddress("2001:db8::3")
        super(Record, records[3]).save()

        ptr_record0.ip_address = None
        super(Record, ptr_record0).save()
        ptr_record1.ip_address = netaddr.IPAddress("10.0.0.4")
        super(Record, ptr_record1).save()
        ptr_record2.ip_address = None
        super(Record, ptr_record2).save()
        ptr_record3.ip_address = netaddr.IPAddress("2001:db8::4")
        super(Record, ptr_record3).save()

        management.call_command("cleanup_database", verbosity=0)

        for record in records:
            record.refresh_from_db()

        ptr_record0 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[0]]
        )
        ptr_record1.refresh_from_db()
        ptr_record2 = Record.objects.get(
            type=RecordTypeChoices.PTR, address_records__in=[records[2]]
        )
        ptr_record3.refresh_from_db()

        self.assertEqual(records[0].ip_address, netaddr.IPAddress("10.0.0.1"))
        self.assertEqual(ptr_record0.ip_address, netaddr.IPAddress("10.0.0.1"))
        self.assertEqual(records[1].ip_address, netaddr.IPAddress("10.0.0.2"))
        self.assertEqual(ptr_record1.ip_address, netaddr.IPAddress("10.0.0.2"))
        self.assertEqual(records[2].ip_address, netaddr.IPAddress("2001:db8::1"))
        self.assertEqual(ptr_record2.ip_address, netaddr.IPAddress("2001:db8::1"))
        self.assertEqual(records[3].ip_address, netaddr.IPAddress("2001:db8::2"))
        self.assertEqual(ptr_record3.ip_address, netaddr.IPAddress("2001:db8::2"))

    def test_remove_orphaned_ptr_records(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        f_zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        r_zone1 = Zone.objects.create(
            name="0.0.10.in-addr.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )
        r_zone2 = Zone.objects.create(
            name="0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        Record.objects.create(
            name="name1", zone=f_zone, type=RecordTypeChoices.A, value="10.0.0.1"
        )
        Record.objects.create(
            name="name2", zone=f_zone, type=RecordTypeChoices.AAAA, value="2001:db8::1"
        )
        Record.objects.create(
            name="2",
            zone=r_zone1,
            type=RecordTypeChoices.PTR,
            value="name3.zone1.example.com.",
            managed=True,
        )
        Record.objects.create(
            name="2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",
            zone=r_zone2,
            type=RecordTypeChoices.PTR,
            value="name4.zone1.example.com.",
            managed=True,
        )

        self.assertTrue(
            Record.objects.filter(
                name="1",
                zone=r_zone1,
                type=RecordTypeChoices.PTR,
                value="name1.zone1.example.com.",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",
                zone=r_zone2,
                type=RecordTypeChoices.PTR,
                value="name2.zone1.example.com.",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="2",
                zone=r_zone1,
                type=RecordTypeChoices.PTR,
                value="name3.zone1.example.com.",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",
                zone=r_zone2,
                type=RecordTypeChoices.PTR,
                value="name4.zone1.example.com.",
            ).exists()
        )

        management.call_command("cleanup_database", verbosity=0)

        self.assertTrue(
            Record.objects.filter(
                name="1",
                zone=r_zone1,
                type=RecordTypeChoices.PTR,
                value="name1.zone1.example.com.",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",
                zone=r_zone2,
                type=RecordTypeChoices.PTR,
                value="name2.zone1.example.com.",
            ).exists()
        )
        self.assertFalse(
            Record.objects.filter(
                name="2",
                zone=r_zone1,
                type=RecordTypeChoices.PTR,
                value="name3.zone1.example.com.",
            ).exists()
        )
        self.assertFalse(
            Record.objects.filter(
                name="2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",
                zone=r_zone2,
                type=RecordTypeChoices.PTR,
                value="name4.zone1.example.com.",
            ).exists()
        )

    def test_remove_orphaned_address_records(self):
        nameserver = NameServer.objects.create(name="ns1.example.com")
        zone = Zone.objects.create(
            name="zone1.example.com",
            soa_mname=nameserver,
            soa_rname="hostmaster.example.com",
        )

        ipv4_prefix = Prefix.objects.create(prefix="10.0.0.0/8")
        ipv6_prefix = Prefix.objects.create(prefix="2001:db8::/32")

        zone.view.prefixes.set([ipv4_prefix, ipv6_prefix])

        IPAddress.objects.create(
            address=IPNetwork("10.0.0.1/24"), dns_name="name1.zone1.example.com"
        )
        IPAddress.objects.create(
            address=IPNetwork("2001:db8::1/64"), dns_name="name2.zone1.example.com"
        )
        Record.objects.create(
            name="name3",
            zone=zone,
            type=RecordTypeChoices.A,
            value="10.0.0.2",
            managed=True,
        )
        Record.objects.create(
            name="name4",
            zone=zone,
            type=RecordTypeChoices.AAAA,
            value="2001:db8::2",
            managed=True,
        )

        self.assertTrue(
            Record.objects.filter(
                name="name1", zone=zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="name2",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="name3", zone=zone, type=RecordTypeChoices.A, value="10.0.0.2"
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="name4",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::2",
            ).exists()
        )

        management.call_command("cleanup_database", verbosity=0)

        self.assertTrue(
            Record.objects.filter(
                name="name1", zone=zone, type=RecordTypeChoices.A, value="10.0.0.1"
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                name="name2",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::1",
            ).exists()
        )
        self.assertFalse(
            Record.objects.filter(
                name="name3", zone=zone, type=RecordTypeChoices.A, value="10.0.0.2"
            ).exists()
        )
        self.assertFalse(
            Record.objects.filter(
                name="name4",
                zone=zone,
                type=RecordTypeChoices.AAAA,
                value="2001:db8::2",
            ).exists()
        )
