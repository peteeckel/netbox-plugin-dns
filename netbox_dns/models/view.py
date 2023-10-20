from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.context import current_request
from utilities.exceptions import AbortRequest

from netbox_dns.mixins import ObjectModificationMixin


__all__ = (
    "View",
    "ViewIndex",
)


class View(ObjectModificationMixin, NetBoxModel):
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
    prefixes = models.ManyToManyField(
        to="ipam.Prefix",
        related_name="netbox_dns_views",
        blank=True,
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

    def delete(self, *args, **kwargs):
        if self.default_view:
            if current_request.get() is not None:
                raise AbortRequest("The default view cannot be deleted")

            raise ValidationError("The default view cannot be deleted")

        super().delete(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if (changed_fields := self.changed_fields) is None:
            return

        if (
            "default_view" in changed_fields
            and not self.default_view
            and not View.objects.filter(default_view=True).exclude(pk=self.pk).exists()
        ):
            raise ValidationError(
                {
                    "default_view": "Please select a different view as default view to change this setting!"
                }
            )

        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()

        changed_fields = self.changed_fields

        super().save(*args, **kwargs)

        if (changed_fields is None and self.default_view) or (
            changed_fields is not None
            and self.default_view
            and "default_view" in changed_fields
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
