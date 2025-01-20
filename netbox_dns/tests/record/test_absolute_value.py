from django.test import TestCase

from netbox_dns.models import NameServer, Zone, Record
from netbox_dns.choices import RecordTypeChoices


class RecordAbsoluteValueTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        zone_data = {
            "soa_mname": NameServer.objects.create(name="ns1.example.com"),
            "soa_rname": "hostmaster.example.com",
        }

        cls.zone = Zone.objects.create(name="zone1.example.com", **zone_data)

    def test_absolute_cname_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.CNAME,
            value="test2.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "test2.zone1.example.com.")

    def test_relative_cname_value(self):
        record = Record.objects.create(
            name="test1", zone=self.zone, type=RecordTypeChoices.CNAME, value="test2"
        )

        self.assertEqual(record.absolute_value, "test2.zone1.example.com.")

    def test_absolute_dname_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.DNAME,
            value="test2.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "test2.zone1.example.com.")

    def test_relative_dname_value(self):
        record = Record.objects.create(
            name="test1", zone=self.zone, type=RecordTypeChoices.DNAME, value="test2"
        )

        self.assertEqual(record.absolute_value, "test2.zone1.example.com.")

    def test_absolute_ns_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.NS,
            value="ns1.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "ns1.zone1.example.com.")

    def test_relative_ns_value(self):
        record = Record.objects.create(
            name="test1", zone=self.zone, type=RecordTypeChoices.NS, value="ns1"
        )

        self.assertEqual(record.absolute_value, "ns1.zone1.example.com.")

    def test_absolute_https_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.HTTPS,
            value="10 www.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "10 www.zone1.example.com.")

    def test_relative_https_value(self):
        record = Record.objects.create(
            name="test1", zone=self.zone, type=RecordTypeChoices.HTTPS, value="10 www"
        )

        self.assertEqual(record.absolute_value, "10 www.zone1.example.com.")

    def test_absolute_srv_value(self):
        record = Record.objects.create(
            name="_ldap._tcp",
            zone=self.zone,
            type=RecordTypeChoices.SRV,
            value="10 60 636 ldap.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "10 60 636 ldap.zone1.example.com.")

    def test_relative_srv_value(self):
        record = Record.objects.create(
            name="_ldap._tcp",
            zone=self.zone,
            type=RecordTypeChoices.SRV,
            value="10 60 636 ldap",
        )

        self.assertEqual(record.absolute_value, "10 60 636 ldap.zone1.example.com.")

    def test_absolute_svcb_value(self):
        record = Record.objects.create(
            name="_dns",
            zone=self.zone,
            type=RecordTypeChoices.SVCB,
            value="1 resolver.zone1.example.com. alpn=dot",
        )

        self.assertEqual(
            record.absolute_value, '1 resolver.zone1.example.com. alpn="dot"'
        )

    def test_relative_svcb_value(self):
        record = Record.objects.create(
            name="_dns",
            zone=self.zone,
            type=RecordTypeChoices.SVCB,
            value="1 resolver alpn=dot",
        )

        self.assertEqual(
            record.absolute_value, '1 resolver.zone1.example.com. alpn="dot"'
        )

    def test_absolute_mx_value(self):
        record = Record.objects.create(
            name="mx",
            zone=self.zone,
            type=RecordTypeChoices.MX,
            value="10 mx1.zone1.example.com.",
        )

        self.assertEqual(record.absolute_value, "10 mx1.zone1.example.com.")

    def test_relative_mx_value(self):
        record = Record.objects.create(
            name="mx", zone=self.zone, type=RecordTypeChoices.MX, value="10 mx1"
        )

        self.assertEqual(record.absolute_value, "10 mx1.zone1.example.com.")

    def test_absolute_rp_value(self):
        record = Record.objects.create(
            name="@",
            zone=self.zone,
            type=RecordTypeChoices.RP,
            value="admin.zone1.example.com. info.admin.zone1.example.com.",
        )

        self.assertEqual(
            record.absolute_value,
            "admin.zone1.example.com. info.admin.zone1.example.com.",
        )

    def test_relative_rp_value(self):
        record = Record.objects.create(
            name="@",
            zone=self.zone,
            type=RecordTypeChoices.RP,
            value="admin info.admin",
        )

        self.assertEqual(
            record.absolute_value,
            "admin.zone1.example.com. info.admin.zone1.example.com.",
        )

    def test_absolute_naptr_value(self):
        record = Record.objects.create(
            name="sip",
            zone=self.zone,
            type=RecordTypeChoices.NAPTR,
            value='100 10 "S" "SIP+D2U" "!^.*$!sip:customer-service@example.com!" _sip._udp.zone1.example.com.',
        )

        self.assertEqual(
            record.absolute_value,
            '100 10 "S" "SIP+D2U" "!^.*$!sip:customer-service@example.com!" _sip._udp.zone1.example.com.',
        )

    def test_relative_naptr_value(self):
        record = Record.objects.create(
            name="sip",
            zone=self.zone,
            type=RecordTypeChoices.NAPTR,
            value='100 10 "S" "SIP+D2U" "!^.*$!sip:customer-service@example.com!" _sip._udp',
        )

        self.assertEqual(
            record.absolute_value,
            '100 10 "S" "SIP+D2U" "!^.*$!sip:customer-service@example.com!" _sip._udp.zone1.example.com.',
        )

    def test_absolute_px_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.PX,
            value="10 test2.zone1.example.com. test3.zone1.example.com.",
        )

        self.assertEqual(
            record.absolute_value,
            "10 test2.zone1.example.com. test3.zone1.example.com.",
        )

    def test_relative_px_value(self):
        record = Record.objects.create(
            name="test1",
            zone=self.zone,
            type=RecordTypeChoices.PX,
            value="10 test2 test3",
        )

        self.assertEqual(
            record.absolute_value,
            "10 test2.zone1.example.com. test3.zone1.example.com.",
        )
