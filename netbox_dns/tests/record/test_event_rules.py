import uuid

from unittest import skipIf
from packaging.version import Version

import django_rq
from django.urls import reverse
from django.test import RequestFactory
from django.conf import settings
from rest_framework import status

from core.models import ObjectType
from extras.models import EventRule, Tag, Webhook
from extras.choices import EventRuleActionChoices, ObjectChangeActionChoices
from extras.context_managers import event_tracking
from utilities.testing import APITestCase

from netbox_dns.models import NameServer, Zone, Record, RecordTypeChoices


class RecordEventRuleTest(APITestCase):
    MIN_VERSION = "4.0.4"

    def setUp(self):
        super().setUp()

        self.queue = django_rq.get_queue("default")
        self.queue.empty()

    @classmethod
    def setUpTestData(cls):
        DUMMY_URL = "http://localhost:9000/"
        DUMMY_SECRET = "THISISNOTASECRETANYMORE"

        record_type = ObjectType.objects.get_for_model(Record)
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        webhooks = (
            Webhook(name="Record Webhook", payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        )
        Webhook.objects.bulk_create(webhooks)

        event_rules = (
            EventRule(
                name="Record Create",
                type_create=True,
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
            ),
            EventRule(
                name="Record Update",
                type_update=True,
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
            ),
            EventRule(
                name="Record Delete",
                type_delete=True,
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
            ),
        )
        EventRule.objects.bulk_create(event_rules)
        for event_rule in event_rules:
            event_rule.object_types.set([record_type])

        cls.tags = (
            Tag(name="Tag 1", slug="tag-1"),
            Tag(name="Tag 2", slug="tag-2"),
            Tag(name="Tag 3", slug="tag-3"),
        )
        Tag.objects.bulk_create(cls.tags)

        nameserver = NameServer.objects.create(name="ns1.example.com")

        zone_data = {
            "soa_mname": nameserver,
            "soa_rname": "hostmaster.example.com",
            "soa_serial": 1,
            "soa_serial_auto": False,
        }

        cls.zones = (
            Zone(name="zone1.example.com", **zone_data),
            Zone(name="0.0.10.in-addr.arpa", **zone_data),
        )
        for zone in cls.zones:
            zone.save()

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_create_record(self):
        url = reverse("plugins:netbox_dns:record_add")
        request = RequestFactory().get(url)
        request.id = uuid.uuid4()
        request.user = self.user

        self.assertEqual(self.queue.count, 0, msg="Unexpected jobs found in queue")

        with event_tracking(request):
            record = Record.objects.create(
                name="name1",
                zone=self.zones[0],
                type=RecordTypeChoices.A,
                value="10.0.0.1",
            )
            record.save()

        self.assertEqual(self.queue.count, 2)

        ptr_job = self.queue.jobs[0]
        self.assertEqual(ptr_job.kwargs["data"]["zone"]["name"], self.zones[1].name)
        self.assertEqual(ptr_job.kwargs["data"]["type"], RecordTypeChoices.PTR)
        self.assertEqual(ptr_job.kwargs["data"]["name"], "1")
        self.assertEqual(
            ptr_job.kwargs["data"]["value"], f"name1.{self.zones[0].name}."
        )
        self.assertIsNone(ptr_job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(ptr_job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["zone"], self.zones[1].pk
        )
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["type"], RecordTypeChoices.PTR
        )
        self.assertEqual(ptr_job.kwargs["snapshots"]["postchange"]["name"], "1")
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["value"],
            f"name1.{self.zones[0].name}.",
        )

        a_job = self.queue.jobs[1]
        self.assertEqual(a_job.kwargs["data"]["zone"]["name"], self.zones[0].name)
        self.assertEqual(a_job.kwargs["data"]["type"], RecordTypeChoices.A)
        self.assertEqual(a_job.kwargs["data"]["name"], "name1")
        self.assertEqual(a_job.kwargs["data"]["value"], "10.0.0.1")
        self.assertIsNone(a_job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(a_job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            a_job.kwargs["snapshots"]["postchange"]["zone"], self.zones[0].pk
        )
        self.assertEqual(
            a_job.kwargs["snapshots"]["postchange"]["type"], RecordTypeChoices.A
        )
        self.assertEqual(a_job.kwargs["snapshots"]["postchange"]["name"], "name1")
        self.assertEqual(a_job.kwargs["snapshots"]["postchange"]["value"], "10.0.0.1")

    def test_update_record(self):
        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        url = reverse(
            "plugins-api:netbox_dns-api:record-detail", kwargs={"pk": record.pk}
        )
        self.add_permissions("netbox_dns.change_record")
        data = {
            "value": "10.0.0.2",
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 2)

        ptr_job = self.queue.jobs[0]
        self.assertEqual(ptr_job.kwargs["data"]["zone"]["name"], self.zones[1].name)
        self.assertEqual(ptr_job.kwargs["data"]["type"], RecordTypeChoices.PTR)
        self.assertEqual(ptr_job.kwargs["data"]["name"], "2")
        self.assertEqual(
            ptr_job.kwargs["data"]["value"], f"name1.{self.zones[0].name}."
        )
        self.assertIsNotNone(ptr_job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["zone"], self.zones[1].pk
        )
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["type"], RecordTypeChoices.PTR
        )
        self.assertEqual(ptr_job.kwargs["snapshots"]["postchange"]["name"], "2")
        self.assertEqual(
            ptr_job.kwargs["snapshots"]["postchange"]["value"],
            f"name1.{self.zones[0].name}.",
        )

        a_job = self.queue.jobs[1]
        self.assertEqual(a_job.kwargs["data"]["zone"]["name"], self.zones[0].name)
        self.assertEqual(a_job.kwargs["data"]["type"], RecordTypeChoices.A)
        self.assertEqual(a_job.kwargs["data"]["name"], "name1")
        self.assertEqual(a_job.kwargs["data"]["value"], "10.0.0.2")
        self.assertIsNotNone(a_job.kwargs["snapshots"].get("prechange"))
        self.assertEqual(
            a_job.kwargs["snapshots"]["prechange"]["zone"], self.zones[0].pk
        )
        self.assertEqual(
            a_job.kwargs["snapshots"]["prechange"]["type"], RecordTypeChoices.A
        )
        self.assertEqual(a_job.kwargs["snapshots"]["prechange"]["name"], "name1")
        self.assertEqual(a_job.kwargs["snapshots"]["prechange"]["value"], "10.0.0.1")
        self.assertIsNotNone(a_job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            a_job.kwargs["snapshots"]["postchange"]["zone"], self.zones[0].pk
        )
        self.assertEqual(
            a_job.kwargs["snapshots"]["postchange"]["type"], RecordTypeChoices.A
        )
        self.assertEqual(a_job.kwargs["snapshots"]["postchange"]["name"], "name1")
        self.assertEqual(a_job.kwargs["snapshots"]["postchange"]["value"], "10.0.0.2")

    def test_update_record_add_tags(self):
        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )

        url = reverse(
            "plugins-api:netbox_dns-api:record-detail", kwargs={"pk": record.pk}
        )
        self.add_permissions("netbox_dns.change_record")
        data = {
            "tags": [
                {"name": self.tags[0].name},
                {"name": self.tags[1].name},
                {"name": self.tags[2].name},
            ],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(len(self.queue.jobs), 1)
        job = self.queue.jobs[0]
        self.assertEqual(len(job.kwargs["data"]["tags"]), 3)
        self.assertIsNotNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(len(job.kwargs["snapshots"]["prechange"]["tags"]), 0)
        self.assertEqual(len(job.kwargs["snapshots"]["postchange"]["tags"]), 3)
        self.assertEqual(
            job.kwargs["snapshots"]["postchange"]["tags"],
            [tag.name for tag in self.tags],
        )

    def test_update_record_remove_tags(self):
        record = Record.objects.create(
            name="name1", zone=self.zones[0], type=RecordTypeChoices.A, value="10.0.0.1"
        )
        record.tags.set(self.tags)

        url = reverse(
            "plugins-api:netbox_dns-api:record-detail", kwargs={"pk": record.pk}
        )
        self.add_permissions("netbox_dns.change_record")
        data = {
            "tags": [{"name": self.tags[0].name}],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(len(self.queue.jobs), 1)
        job = self.queue.jobs[0]
        self.assertEqual(len(job.kwargs["data"]["tags"]), 1)
        self.assertIsNotNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(len(job.kwargs["snapshots"]["prechange"]["tags"]), 3)
        self.assertEqual(
            job.kwargs["snapshots"]["prechange"]["tags"],
            [tag.name for tag in self.tags],
        )
        self.assertEqual(len(job.kwargs["snapshots"]["postchange"]["tags"]), 1)
        self.assertEqual(
            job.kwargs["snapshots"]["postchange"]["tags"], [self.tags[0].name]
        )
