from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search

from taggit.managers import TaggableManager


class Contact(NetBoxModel):
    # +
    # Data fields according to https://www.icann.org/resources/pages/rdds-labeling-policy-2017-02-01-en
    # -
    contact_id = models.CharField(
        verbose_name="Contact ID",
        max_length=50,
        unique=True,
    )
    name = models.CharField(
        blank=True,
        max_length=100,
    )
    organization = models.CharField(
        blank=True,
        max_length=200,
    )
    street = models.CharField(
        blank=True,
        max_length=50,
    )
    city = models.CharField(
        blank=True,
        max_length=50,
    )
    state_province = models.CharField(
        verbose_name="State/Province",
        blank=True,
        max_length=255,
    )
    postal_code = models.CharField(
        verbose_name="Postal Code",
        blank=True,
        max_length=20,
    )
    country = models.CharField(
        verbose_name="Country (ISO 3166)",
        blank=True,
        max_length=2,
    )
    phone = models.CharField(
        verbose_name="Phone",
        blank=True,
        max_length=50,
    )
    phone_ext = models.CharField(
        verbose_name="Phone Extension",
        blank=True,
        max_length=50,
    )
    fax = models.CharField(
        verbose_name="Fax",
        blank=True,
        max_length=50,
    )
    fax_ext = models.CharField(
        verbose_name="Fax Extension",
        blank=True,
        max_length=50,
    )
    email = models.EmailField(
        verbose_name="Email",
        blank=True,
    )

    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="netbox_dns_contact_set",
    )

    clone_fields = [
        "name",
        "organization",
        "street",
        "city",
        "state_province",
        "postal_code",
        "country",
        "phone",
        "phone_ext",
        "fax",
        "fax_ext",
        "email",
        "tags",
    ]

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:contact", kwargs={"pk": self.id})

    def __str__(self):
        if self.name is not None:
            return f"{self.contact_id} ({self.name})"

        return self.contact_id

    class Meta:
        ordering = ("name", "contact_id")

    @property
    def zones(self):
        return (
            set(self.zone_set.all())
            | set(self.admin_c_zones.all())
            | set(self.tech_c_zones.all())
            | set(self.billing_c_zones.all())
        )


@register_search
class ContactIndex(SearchIndex):
    model = Contact
    fields = (
        ("name", 100),
        ("contact_id", 100),
        ("email", 200),
        ("organization", 500),
    )
