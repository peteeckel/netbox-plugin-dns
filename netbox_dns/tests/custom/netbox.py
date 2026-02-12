import inspect

import strawberry_django

from django.urls import reverse
from django.utils.module_loading import import_string

from strawberry.types.base import StrawberryList, StrawberryOptional
from strawberry.types.union import StrawberryUnion
from strawberry.types.lazy_type import LazyType

from ipam.graphql.types import IPAddressFamilyType
from utilities.testing.api import APITestCase as NetBoxAPITestCase
from utilities.testing.views import ModelViewTestCase as NetBoxModelViewTestCase
from netbox.api.exceptions import GraphQLTypeNotFound

__all__ = (
    "NetBoxDNSGraphQLMixin",
    "ModelViewTestCase",
    "APITestCase",
)


def get_graphql_type_for_model(model):
    app_label, model_name = model._meta.label.split(".")
    class_name = f"{app_label}.graphql.types.NetBoxDNS{model_name}Type"
    try:
        return import_string(class_name)
    except ImportError:
        raise GraphQLTypeNotFound(
            f"Could not find GraphQL type for {app_label}.{model_name}"
        )


class NetBoxDNSGraphQLMixin:
    def _get_graphql_base_name(self):
        base_name = self.model._meta.verbose_name.lower().replace(" ", "_")
        return getattr(self, "graphql_base_name", f"netbox_dns_{base_name}")

    def _build_query(self, name, **filters):
        type_class = get_graphql_type_for_model(self.model)
        if filters:
            filter_string = ", ".join(f"{k}:{v}" for k, v in filters.items())
            filter_string = f"({filter_string})"
        else:
            filter_string = ""

        # Compile list of fields to include
        fields_string = ""

        file_fields = (
            strawberry_django.fields.types.DjangoFileType,
            strawberry_django.fields.types.DjangoImageType,
        )
        for field in type_class.__strawberry_definition__.fields:
            if field.type in file_fields or (
                isinstance(field.type, StrawberryOptional)
                and field.type.of_type in file_fields
            ):
                # image / file fields nullable or not...
                fields_string += f"{field.name} {{ name }}\n"
            elif isinstance(field.type, StrawberryList) and isinstance(
                field.type.of_type, LazyType
            ):
                # List of related objects (queryset)
                fields_string += f"{field.name} {{ id }}\n"
            elif isinstance(field.type, StrawberryList) and isinstance(
                field.type.of_type, StrawberryUnion
            ):
                # this would require a fragment query
                continue
            elif isinstance(field.type, StrawberryUnion):
                # this would require a fragment query
                continue
            elif isinstance(field.type, StrawberryOptional) and isinstance(
                field.type.of_type, LazyType
            ):
                fields_string += f"{field.name} {{ id }}\n"
            elif hasattr(field, "is_relation") and field.is_relation:
                # Note: StrawberryField types do not have is_relation
                fields_string += f"{field.name} {{ id }}\n"
            elif inspect.isclass(field.type) and issubclass(
                field.type, IPAddressFamilyType
            ):
                fields_string += f"{field.name} {{ value, label }}\n"
            else:
                fields_string += f"{field.name}\n"

        query = f"""
        {{
            {name}{filter_string} {{
                {fields_string}
            }}
        }}
        """

        return query


class ModelViewTestCase(NetBoxModelViewTestCase):
    def _get_base_url(self):
        return (
            f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"
        )


class APITestCase(NetBoxAPITestCase):
    def _get_detail_url(self, instance):
        viewname = f"plugins-api:{self._get_view_namespace()}:{instance._meta.model_name}-detail"
        return reverse(viewname, kwargs={"pk": instance.pk})

    def _get_list_url(self):
        viewname = f"plugins-api:{self._get_view_namespace()}:{self.model._meta.model_name}-list"
        return reverse(viewname)
