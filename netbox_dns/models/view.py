from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search


class View(NetBoxModel):
    name = models.CharField(
        unique=True,
        max_length=255,
    )
    description = models.CharField(
        max_length=200,
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

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:view", kwargs={"pk": self.id})

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ("name",)


@register_search
class ViewIndex(SearchIndex):
    model = View
    fields = (
        ("name", 100),
        ("description", 500),
    )
