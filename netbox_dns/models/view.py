from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.context import current_request
from utilities.exceptions import AbortRequest


class View(NetBoxModel):
    name = models.CharField(
        unique=True,
        max_length=255,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    default_view = models.BooleanField(
        default=False,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_views",
        blank=True,
        null=True,
    )

    clone_fields = ["name", "description"]

    @classmethod
    def get_default_view(cls):
        return cls.objects.get(default_view=True)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:view", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ("name",)

    def delete(self):
        if self.default_view:
            if current_request.get() is not None:
                raise AbortRequest("The default view cannot be deleted")

            raise ValidationError("The default view cannot be deleted")

        super().delete()

    def clean(self, *args, old_state=None, **kwargs):
        if self.pk is None:
            return

        old_state = View.objects.get(pk=self.pk)

        if (
            old_state.default_view
            and not self.default_view
            and not View.objects.filter(default_view=True).exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                {
                    "default_view": "Please select a different view as default view to change this setting!"
                }
            )

    def save(self, *args, **kwargs):
        self.clean()

        old_state = None if self.pk is None else View.objects.get(pk=self.pk)

        super().save()

        if (old_state is None and self.default_view) or (
            old_state is not None and self.default_view and not old_state.default_view
        ):
            other_views = View.objects.filter(default_view=True).exclude(pk=self.pk)
            for view in other_views:
                view.default_view = False
                view.save()


@register_search
class ViewIndex(SearchIndex):
    model = View
    fields = (
        ("name", 100),
        ("description", 500),
    )
