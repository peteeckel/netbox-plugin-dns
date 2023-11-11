import django_tables2 as tables

from netbox.tables import NetBoxTable, TagColumn

from netbox_dns.models import Contact


class ContactTable(NetBoxTable):
    contact_id = tables.Column(
        linkify=True,
    )
    tags = TagColumn(
        url_name="plugins:netbox_dns:contact_list",
    )

    class Meta(NetBoxTable.Meta):
        model = Contact
        fields = (
            "contact_id",
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
        )
        default_columns = ("contact_id", "name", "email")
