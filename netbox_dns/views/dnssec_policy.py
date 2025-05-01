from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from netbox_dns.filtersets import (
    DNSSECPolicyFilterSet,
    ZoneFilterSet,
    ZoneTemplateFilterSet,
)
from netbox_dns.forms import (
    DNSSECPolicyImportForm,
    DNSSECPolicyFilterForm,
    DNSSECPolicyForm,
    DNSSECPolicyBulkEditForm,
)
from netbox_dns.models import DNSSECPolicy, Zone, ZoneTemplate
from netbox_dns.tables import (
    DNSSECPolicyTable,
    ZoneDisplayTable,
    ZoneTemplateDisplayTable,
)
from netbox_dns.validators import validate_key_template_lifetime
from netbox_dns.choices import DNSSECKeyTemplateTypeChoices


__all__ = (
    "DNSSECPolicyView",
    "DNSSECPolicyListView",
    "DNSSECPolicyEditView",
    "DNSSECPolicyDeleteView",
    "DNSSECPolicyBulkEditView",
    "DNSSECPolicyBulkImportView",
    "DNSSECPolicyBulkDeleteView",
)


@register_model_view(DNSSECPolicy, "list", path="", detail=False)
class DNSSECPolicyListView(generic.ObjectListView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    filterset_form = DNSSECPolicyFilterForm
    table = DNSSECPolicyTable


@register_model_view(DNSSECPolicy)
class DNSSECPolicyView(generic.ObjectView):
    queryset = DNSSECPolicy.objects.prefetch_related(
        "key_templates", "zones", "zone_templates"
    )

    def get_extra_context(self, request, instance):
        context = {}

        key_errors = {
            key_template.pk: validate_key_template_lifetime(key_template, instance)
            for key_template in instance.key_templates.all()
        }

        context["key_template_errors"] = key_errors

        if not instance.key_templates.filter(
            type__in=(
                DNSSECKeyTemplateTypeChoices.TYPE_ZSK,
                DNSSECKeyTemplateTypeChoices.TYPE_CSK,
            )
        ).exists():
            context["policy_warning"] = _(
                "No key for signing zones (CSK or ZSK) is assigned."
            )

        return context


@register_model_view(DNSSECPolicy, "add", detail=False)
@register_model_view(DNSSECPolicy, "edit")
class DNSSECPolicyEditView(generic.ObjectEditView):
    queryset = DNSSECPolicy.objects.all()
    form = DNSSECPolicyForm


@register_model_view(DNSSECPolicy, "delete")
class DNSSECPolicyDeleteView(generic.ObjectDeleteView):
    queryset = DNSSECPolicy.objects.all()


@register_model_view(DNSSECPolicy, "bulk_import", detail=False)
class DNSSECPolicyBulkImportView(generic.BulkImportView):
    queryset = DNSSECPolicy.objects.all()
    model_form = DNSSECPolicyImportForm
    table = DNSSECPolicyTable


@register_model_view(DNSSECPolicy, "bulk_edit", path="edit", detail=False)
class DNSSECPolicyBulkEditView(generic.BulkEditView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    table = DNSSECPolicyTable
    form = DNSSECPolicyBulkEditForm


@register_model_view(DNSSECPolicy, "bulk_delete", path="delete", detail=False)
class DNSSECPolicyBulkDeleteView(generic.BulkDeleteView):
    queryset = DNSSECPolicy.objects.all()
    filterset = DNSSECPolicyFilterSet
    table = DNSSECPolicyTable


@register_model_view(DNSSECPolicy, "zones")
class DNSSECPolicyZoneListView(generic.ObjectChildrenView):
    queryset = DNSSECPolicy.objects.all()
    child_model = Zone
    table = ZoneDisplayTable
    filterset = ZoneFilterSet
    template_name = "netbox_dns/zone/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("Zones"),
        permission="netbox_dns.view_zones",
        badge=lambda obj: obj.zones.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zones.restrict(request.user, "view")


@register_model_view(DNSSECPolicy, "zonetemplates")
class DNSSECPolicyZoneTemplateListView(generic.ObjectChildrenView):
    queryset = DNSSECPolicy.objects.all()
    child_model = ZoneTemplate
    table = ZoneTemplateDisplayTable
    filterset = ZoneTemplateFilterSet
    template_name = "netbox_dns/zonetemplate/child.html"
    hide_if_empty = True

    tab = ViewTab(
        label=_("Zone Templates"),
        permission="netbox_dns.view_zonetemplates",
        badge=lambda obj: obj.zone_templates.count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.zone_templates.restrict(request.user, "view")
