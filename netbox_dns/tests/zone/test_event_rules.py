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

from netbox_dns.models import NameServer, Zone


class ZoneEventRuleTest(APITestCase):
    MIN_VERSION = "4.0.4"

    def setUp(self):
        super().setUp()

        self.queue = django_rq.get_queue("default")
        self.queue.empty()

    @classmethod
    def setUpTestData(cls):
        DUMMY_URL = "http://localhost:9000/"
        DUMMY_SECRET = "THISISNOTASECRETANYMORE"

        zone_type = ObjectType.objects.get_for_model(Zone)
        webhook_type = ObjectType.objects.get_for_model(Webhook)

        webhooks = (
            Webhook(name="Zone Webhook", payload_url=DUMMY_URL, secret=DUMMY_SECRET),
        )
        Webhook.objects.bulk_create(webhooks)

        event_rules = (
            EventRule(
                name="Zone Create",
                type_create=True,
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
            ),
            EventRule(
                name="Zone Update",
                type_update=True,
                action_type=EventRuleActionChoices.WEBHOOK,
                action_object_type=webhook_type,
                action_object_id=webhooks[0].id,
            ),
        )
        EventRule.objects.bulk_create(event_rules)
        for event_rule in event_rules:
            event_rule.object_types.set([zone_type])

        cls.tags = (
            Tag(name="Tag 1", slug="tag-1"),
            Tag(name="Tag 2", slug="tag-2"),
            Tag(name="Tag 3", slug="tag-3"),
        )
        Tag.objects.bulk_create(cls.tags)

        cls.nameservers = (
            NameServer(name="ns1.example.com"),
            NameServer(name="ns2.example.com"),
            NameServer(name="ns3.example.com"),
        )
        NameServer.objects.bulk_create(cls.nameservers)

        cls.zone_data = {
            "soa_mname": cls.nameservers[0],
            "soa_rname": "hostmaster.example.com",
        }

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_create_zone(self):
        url = reverse("plugins:netbox_dns:zone_add")
        request = RequestFactory().get(url)
        request.id = uuid.uuid4()
        request.user = self.user

        self.assertEqual(self.queue.count, 0, msg="Unexpected jobs found in queue")

        with event_tracking(request):
            zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)
            zone.save()

        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(
            job.kwargs["data"]["soa_mname"]["name"], self.nameservers[0].name
        )
        self.assertEqual(
            job.kwargs["data"]["soa_rname"], self.zone_data.get("soa_rname")
        )
        self.assertIsNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            job.kwargs["snapshots"]["postchange"]["soa_mname"], self.nameservers[0].pk
        )
        self.assertEqual(
            job.kwargs["snapshots"]["postchange"]["soa_rname"],
            self.zone_data.get("soa_rname"),
        )

    def test_update_zone(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)

        self.assertEqual(self.queue.count, 0, msg="Unexpected jobs found in queue")

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})
        self.add_permissions("netbox_dns.change_zone")
        data = {
            "soa_refresh": 86400,
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(job.kwargs["data"]["soa_refresh"], 86400)
        self.assertIsNotNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(
            job.kwargs["snapshots"]["prechange"]["soa_refresh"],
            Zone.get_defaults()["soa_refresh"],
        )
        self.assertEqual(job.kwargs["snapshots"]["postchange"]["soa_refresh"], 86400)

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_update_zone_add_nameservers(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)

        self.assertEqual(self.queue.count, 0, msg="Unexpected jobs found in queue")

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})
        self.add_permissions("netbox_dns.change_zone")
        data = {
            "nameservers": [
                {"name": self.nameservers[1].name},
                {"name": self.nameservers[2].name},
            ],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(len(job.kwargs["data"]["nameservers"]), 2)
        self.assertIsNotNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(len(job.kwargs["snapshots"]["prechange"]["nameservers"]), 0)
        self.assertEqual(len(job.kwargs["snapshots"]["postchange"]["nameservers"]), 2)
        self.assertEqual(
            job.kwargs["snapshots"]["postchange"]["nameservers"],
            [nameserver.pk for nameserver in self.nameservers[1:]],
        )

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_update_zone_remove_nameservers(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)
        zone.nameservers.set(self.nameservers[1:])

        self.assertEqual(self.queue.count, 0, msg="Unexpected jobs found in queue")

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})
        self.add_permissions("netbox_dns.change_zone")
        data = {
            "nameservers": [],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 1)
        job = self.queue.jobs[0]
        self.assertEqual(len(job.kwargs["data"]["nameservers"]), 0)
        self.assertIsNotNone(job.kwargs["snapshots"].get("prechange"))
        self.assertIsNotNone(job.kwargs["snapshots"].get("postchange"))
        self.assertEqual(len(job.kwargs["snapshots"]["prechange"]["nameservers"]), 2)
        self.assertEqual(
            job.kwargs["snapshots"]["prechange"]["nameservers"],
            [nameserver.pk for nameserver in self.nameservers[1:]],
        )
        self.assertEqual(len(job.kwargs["snapshots"]["postchange"]["nameservers"]), 0)

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_update_zone_add_tags(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})
        self.add_permissions("netbox_dns.change_zone")
        data = {
            "tags": [
                {"name": self.tags[0].name},
                {"name": self.tags[1].name},
                {"name": self.tags[2].name},
            ],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 1)
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

    @skipIf(
        Version(settings.VERSION) < Version(MIN_VERSION),
        f"Event rule processing is broken in NetBox < {MIN_VERSION}",
    )
    def test_update_zone_remove_tags(self):
        zone = Zone.objects.create(name="zone1.example.com", **self.zone_data)
        zone.tags.set(self.tags)

        url = reverse("plugins-api:netbox_dns-api:zone-detail", kwargs={"pk": zone.pk})
        self.add_permissions("netbox_dns.change_zone")
        data = {
            "tags": [{"name": self.tags[0].name}],
        }
        response = self.client.patch(url, data, format="json", **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        self.assertEqual(self.queue.count, 1)
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
