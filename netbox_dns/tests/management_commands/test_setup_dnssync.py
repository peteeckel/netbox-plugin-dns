from django.test import TestCase
from django.core import management

from core.models import ObjectType
from extras.models import CustomField
from extras.choices import CustomFieldTypeChoices
from ipam.models import IPAddress


class NetBoxDNSManagementSetupDNSsyncTestCase(TestCase):
    def test_setup_dnssync(self):
        management.call_command("setup_dnssync", verbosity=0)

        ipaddress_object_type = ObjectType.objects.get_for_model(IPAddress)

        for cf_name in (
            "ipaddress_dns_disabled",
            "ipaddress_dns_record_ttl",
            "ipaddress_dns_record_disable_ptr",
        ):
            self.assertTrue(
                CustomField.objects.filter(
                    name=cf_name, object_types=ipaddress_object_type
                ).exists()
            )

        dns_disabled_cf = CustomField.objects.get(name="ipaddress_dns_disabled")
        self.assertEqual(dns_disabled_cf.type, CustomFieldTypeChoices.TYPE_BOOLEAN)
        self.assertFalse(dns_disabled_cf.required)
        self.assertFalse(dns_disabled_cf.default)

        dns_record_ttl_cf = CustomField.objects.get(name="ipaddress_dns_record_ttl")
        self.assertEqual(dns_record_ttl_cf.type, CustomFieldTypeChoices.TYPE_INTEGER)
        self.assertFalse(dns_record_ttl_cf.required)

        dns_record_disable_ptr_cf = CustomField.objects.get(
            name="ipaddress_dns_record_disable_ptr"
        )
        self.assertEqual(
            dns_record_disable_ptr_cf.type, CustomFieldTypeChoices.TYPE_BOOLEAN
        )
        self.assertFalse(dns_record_disable_ptr_cf.required)
        self.assertFalse(dns_record_disable_ptr_cf.default)

    def test_setup_dnssync_remove(self):
        management.call_command("setup_dnssync", verbosity=0)

        ipaddress_object_type = ObjectType.objects.get_for_model(IPAddress)

        for cf_name in (
            "ipaddress_dns_disabled",
            "ipaddress_dns_record_ttl",
            "ipaddress_dns_record_disable_ptr",
        ):
            self.assertTrue(
                CustomField.objects.filter(
                    name=cf_name, object_types=ipaddress_object_type
                ).exists()
            )

        management.call_command("setup_dnssync", verbosity=0, remove=True)

        for cf_name in (
            "ipaddress_dns_disabled",
            "ipaddress_dns_record_ttl",
            "ipaddress_dns_record_disable_ptr",
        ):
            self.assertFalse(
                CustomField.objects.filter(
                    name=cf_name, object_types=ipaddress_object_type
                ).exists()
            )
