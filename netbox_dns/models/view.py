from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError

from netbox.models import NetBoxModel
from netbox.models.features import ContactsMixin
from netbox.search import SearchIndex, register_search
from netbox.context import current_request
from utilities.exceptions import AbortRequest

from netbox_dns.mixins import ObjectModificationMixin
from netbox_dns.utilities import (
    get_ip_addresses_by_view,
    check_dns_records,
    update_dns_records,
    delete_dns_records,
    get_query_from_filter,
)


__all__ = (
    "View",
    "ViewIndex",
)


class View(ObjectModificationMixin, ContactsMixin, NetBoxModel):
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
    ip_address_filter = models.JSONField(
        verbose_name="IP Address Filter",
        blank=True,
        null=True,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_views",
        blank=True,
        null=True,
    )

    clone_fields = (
        "name",
        "description",
    )

    @classmethod
    def get_default_view(cls):
        return cls.objects.get(default_view=True)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:view", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"

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

        if "ip_address_filter" in changed_fields and self.get_saved_value(
            "ip_address_filter"
        ):
            try:
                for ip_address in get_ip_addresses_by_view(self).filter(
                    get_query_from_filter(self.ip_address_filter)
                ):
                    check_dns_records(ip_address, view=self)
            except ValidationError as exc:
                raise ValidationError(
                    {
                        "ip_address_filter": exc.messages,
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

        if changed_fields is not None and "ip_address_filter" in changed_fields:
            ip_addresses = get_ip_addresses_by_view(self)

            for ip_address in ip_addresses.exclude(
                get_query_from_filter(self.ip_address_filter)
            ):
                delete_dns_records(ip_address, view=self)

            for ip_address in ip_addresses.filter(
                get_query_from_filter(self.ip_address_filter)
            ):
                update_dns_records(ip_address, view=self)


@register_search
class ViewIndex(SearchIndex):
    model = View
    fields = (
        ("name", 100),
        ("description", 500),
    )
