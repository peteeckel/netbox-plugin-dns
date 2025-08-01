from netaddr import IPNetwork

from django.test import TestCase
from django.core import management

from ipam.models import IPAddress, Prefix

from netbox_dns.models import View, Zone, Record, NameServer
from netbox_dns.choices import RecordTypeChoices


class NetBoxDNSManagementRebuildDNSsyncTestCase(TestCase):
    def test_rebuild_dnssync(self):
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

        prefix = Prefix.objects.create(prefix="2001:db8::/32")

        zone.view.prefixes.add(prefix)

        ip_addresses = (
            IPAddress(
                address=IPNetwork("2001:db8::1/64"), dns_name="name1.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::2/64"), dns_name="name2.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::3/64"), dns_name="name3.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::4/64"), dns_name="name4.zone1.example.com"
            ),
        )
        for ip_address in ip_addresses:
            ip_address.save()

        for ip_address in ip_addresses:
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.AAAA,
                    fqdn=f"{ip_address.dns_name}.",
                    value=ip_address.address.ip,
                ).exists()
            )
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.PTR, value=f"{ip_address.dns_name}."
                ).exists()
            )

        for ip_address in ip_addresses:
            for record in ip_address.netbox_dns_records.all():
                record.name = "invalid.name"
                record.value = "::1"
                record.save()

            self.assertFalse(
                Record.objects.filter(
                    type=RecordTypeChoices.AAAA,
                    fqdn=f"{ip_address.dns_name}.",
                    value=ip_address.address.ip,
                ).exists()
            )
            self.assertFalse(
                Record.objects.filter(
                    type=RecordTypeChoices.PTR, value=f"{ip_address.dns_name}."
                ).exists()
            )

        self.assertEqual(
            Record.objects.filter(
                type=RecordTypeChoices.AAAA, name="invalid.name"
            ).count(),
            4,
        )
        self.assertEqual(
            Record.objects.filter(type=RecordTypeChoices.AAAA, value="::1").count(), 4
        )
        self.assertFalse(Record.objects.filter(type=RecordTypeChoices.PTR).exists())

        management.call_command("rebuild_dnssync", verbosity=0)

        for ip_address in ip_addresses:
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.AAAA,
                    fqdn=f"{ip_address.dns_name}.",
                    value=ip_address.address.ip,
                ).exists()
            )
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.PTR, value=f"{ip_address.dns_name}."
                ).exists()
            )

        self.assertFalse(
            Record.objects.filter(
                type=RecordTypeChoices.AAAA, name="invalid.name"
            ).exists()
        )
        self.assertFalse(
            Record.objects.filter(type=RecordTypeChoices.AAAA, value="::1").exists()
        )
        self.assertFalse(
            Record.objects.filter(
                type=RecordTypeChoices.PTR, value__startswith="invalid.name"
            ).exists()
        )

    def test_rebuild_dnssync_with_filter(self):
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

        prefix = Prefix.objects.create(prefix="2001:db8::/32")

        zone.view.prefixes.add(prefix)

        ip_addresses = (
            IPAddress(
                address=IPNetwork("2001:db8::1/64"), dns_name="name1.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::2/64"), dns_name="name2.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::3/64"), dns_name="name3.zone1.example.com"
            ),
            IPAddress(
                address=IPNetwork("2001:db8::4/64"), dns_name="name4.zone1.example.com"
            ),
        )
        for ip_address in ip_addresses:
            ip_address.save()

        zone.view.ip_address_filter = {"dns_name__startswith": "name1."}
        super(View, zone.view).save()

        for ip_address in ip_addresses:
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.AAAA,
                    fqdn=f"{ip_address.dns_name}.",
                    value=ip_address.address.ip,
                ).exists()
            )
            self.assertTrue(
                Record.objects.filter(
                    type=RecordTypeChoices.PTR, value=f"{ip_address.dns_name}."
                ).exists()
            )

        management.call_command("rebuild_dnssync", verbosity=0)

        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.AAAA,
                fqdn="name1.zone1.example.com.",
                value="2001:db8::1",
            ).exists()
        )
        self.assertTrue(
            Record.objects.filter(
                type=RecordTypeChoices.PTR, value="name1.zone1.example.com."
            ).exists()
        )
        for ip_address in ip_addresses[1:]:
            self.assertFalse(
                Record.objects.filter(
                    type=RecordTypeChoices.AAAA,
                    fqdn=f"{ip_address.dns_name}.",
                    value=ip_address.address.ip,
                ).exists()
            )
            self.assertFalse(
                Record.objects.filter(
                    type=RecordTypeChoices.PTR, value=f"{ip_address.dns_name}."
                ).exists()
            )
