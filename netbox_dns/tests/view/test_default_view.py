from django.test import TestCase
from django.core.exceptions import ValidationError


from netbox_dns.models import View


class ViewDefaultViewCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.views = (
            View(name="test1"),
            View(name="test2"),
            View(name="test3"),
        )
        View.objects.bulk_create(cls.views)

    def test_default_view_exists(self):
        default_view = View.get_default_view()

        self.assertIsNotNone(default_view)
        self.assertTrue(default_view.default_view)
        self.assertFalse(
            View.objects.filter(default_view=True).exclude(pk=default_view.pk).exists()
        )

    def test_default_view_delete_failure(self):
        default_view = View.get_default_view()

        self.assertIsNotNone(default_view)
        self.assertTrue(default_view.default_view)

        with self.assertRaises(ValidationError):
            default_view.delete()

        self.assertTrue(
            View.objects.filter(default_view=True, pk=default_view.pk).exists()
        )
        self.assertFalse(
            View.objects.filter(default_view=True).exclude(pk=default_view.pk).exists()
        )

    def test_view_delete_success(self):
        view = self.views[0]

        self.assertFalse(view.default_view)

        view_id = view.pk
        view.delete()

        self.assertFalse(View.objects.filter(pk=view_id).exists())

    def test_change_default_view(self):
        default_view = View.get_default_view()
        view = self.views[0]

        self.assertTrue(default_view.default_view)
        self.assertFalse(view.default_view)

        view.default_view = True
        view.save()
        default_view.refresh_from_db()

        self.assertFalse(default_view.default_view)
        self.assertTrue(view.default_view)

    def test_disable_default_view_failure(self):
        default_view = View.get_default_view()

        self.assertTrue(default_view.default_view)

        default_view.default_view = False
        with self.assertRaises(ValidationError):
            default_view.save()

        default_view.refresh_from_db()

        self.assertTrue(default_view.default_view)
        self.assertFalse(
            View.objects.filter(default_view=True).exclude(pk=default_view.pk).exists()
        )

    def test_create_new_default_view(self):
        default_view = View.get_default_view()

        self.assertTrue(default_view.default_view)
        self.assertFalse(
            View.objects.filter(default_view=True).exclude(pk=default_view.pk).exists()
        )

        view = View.objects.create(
            name="New Default View",
            default_view=True,
        )

        default_view.refresh_from_db()

        self.assertFalse(default_view.default_view)
        self.assertTrue(view.default_view)
        self.assertFalse(
            View.objects.filter(default_view=True).exclude(pk=view.pk).exists()
        )
