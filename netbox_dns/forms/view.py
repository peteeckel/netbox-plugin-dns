from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError, FieldError
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _

from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
    NetBoxModelForm,
)
from utilities.forms.fields import (
    TagFilterField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.rendering import FieldSet
from utilities.forms.fields import JSONField
from tenancy.models import Tenant, TenantGroup
from tenancy.forms import TenancyForm, TenancyFilterForm
from ipam.models import Prefix, IPAddress
from netbox.context import current_request

from netbox_dns.models import View
from netbox_dns.fields import PrefixDynamicModelMultipleChoiceField
from netbox_dns.utilities import (
    check_dns_records,
    get_ip_addresses_by_prefix,
    get_views_by_prefix,
    get_query_from_filter,
)


__all__ = (
    "ViewForm",
    "ViewFilterForm",
    "ViewImportForm",
    "ViewBulkEditForm",
    "ViewPrefixEditForm",
)


class ViewPrefixUpdateMixin:
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

        if self.instance._state.adding or "prefixes" not in self.changed_data:
            return

        prefixes = self.cleaned_data.get("prefixes")
        old_prefixes = View.objects.get(pk=self.instance.pk).prefixes.all()

        for prefix in prefixes.difference(old_prefixes):
            for ip_address in get_ip_addresses_by_prefix(prefix, check_view=False):
                try:
                    check_dns_records(ip_address, view=self.instance)
                except ValidationError as exc:
                    self.add_error("prefixes", exc.messages)

        # +
        # Determine the prefixes that, when removed from the view, have no direct view
        # assignment left. These prefixes will potentially inherit from a different view,
        # which means that they have to be validated against different zones.
        # -
        check_prefixes = set(
            old_prefixes.annotate(view_count=Count("netbox_dns_views")).filter(
                Q(view_count=1, netbox_dns_views=self.instance)
                | Q(netbox_dns_views__isnull=True)
            )
        ) - set(prefixes)

        for check_prefix in check_prefixes:
            # +
            # Check whether the prefix will get a new view by inheritance from its
            # parent. If that's the case, the IP addresses need to be checked.
            # -
            if (parent := check_prefix.get_parents().last()) is None:
                continue

            for view in get_views_by_prefix(parent):
                if view == self.instance:
                    continue

                for ip_address in get_ip_addresses_by_prefix(
                    check_prefix, check_view=False
                ):
                    try:
                        check_dns_records(ip_address, view=view)
                    except ValidationError as exc:
                        self.add_error("prefixes", exc.messages)


class ViewForm(ViewPrefixUpdateMixin, TenancyForm, NetBoxModelForm):
    class Meta:
        model = View

        fields = (
            "name",
            "default_view",
            "description",
            "prefixes",
            "ip_address_filter",
            "tenant_group",
            "tenant",
            "tags",
        )

    fieldsets = (
        FieldSet(
            "name",
            "default_view",
            "description",
            name=_("View"),
        ),
        FieldSet(
            "prefixes",
            "ip_address_filter",
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
        FieldSet(
            "tags",
            name=_("Tags"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.PLUGINS_CONFIG["netbox_dns"].get("dnssync_disabled"):
            del self.fields["prefixes"]
            del self.fields["ip_address_filter"]

        if request := current_request.get():
            if not request.user.has_perm("ipam.view_prefix"):
                self._saved_prefixes = self.initial["prefixes"]
                self.initial["prefixes"] = []
                self.fields["prefixes"].disabled = True
                self.fields["prefixes"].widget.attrs["placeholder"] = _(
                    "You do not have permission to modify assigned prefixes"
                )

    prefixes = PrefixDynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        context={
            "depth": None,
        },
        label=_("IPAM Prefixes"),
    )
    ip_address_filter = JSONField(
        required=False,
        help_text=_("Specify criteria for address record creation in JSON form"),
        label=_("IP Address Filter"),
    )

    def clean_prefixes(self):
        if hasattr(self, "_saved_prefixes"):
            return self._saved_prefixes

        return self.cleaned_data["prefixes"]

    def clean_ip_address_filter(self):
        ip_address_filter = self.cleaned_data.get("ip_address_filter")

        try:
            IPAddress.objects.filter(get_query_from_filter(ip_address_filter)).exists()
        except (FieldError, ValueError) as exc:
            self.add_error(
                "ip_address_filter",
                _("Invalid filter for IPAddress: {error}").format(error=exc),
            )

        return ip_address_filter


class ViewFilterForm(TenancyFilterForm, NetBoxModelFilterSetForm):
    model = View

    fieldsets = (
        FieldSet(
            "q",
            "filter_id",
            "tag",
        ),
        FieldSet(
            "name",
            "default_view",
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "prefix_id",
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name=_("Tenancy"),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.PLUGINS_CONFIG["netbox_dns"].get("dnssync_disabled"):
            del self.fields["prefix_id"]

    name = forms.CharField(
        required=False,
    )
    default_view = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )
    description = forms.CharField(
        required=False,
    )
    prefix_id = PrefixDynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        context={
            "depth": None,
        },
        label=_("Prefix"),
    )
    tag = TagFilterField(View)


class ViewImportForm(ViewPrefixUpdateMixin, NetBoxModelImportForm):
    class Meta:
        model = View

        fields = (
            "name",
            "description",
            "prefixes",
            "tenant",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if settings.PLUGINS_CONFIG["netbox_dns"].get("dnssync_disabled"):
            del self.fields["prefixes"]

    prefixes = CSVModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        to_field_name="id",
        required=False,
        help_text=_("Prefix IDs assigned to the view"),
        label=_("Prefixes"),
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        required=False,
        label=_("Tenant"),
    )


class ViewBulkEditForm(NetBoxModelBulkEditForm):
    model = View

    fieldsets = (
        FieldSet(
            "description",
            name=_("Attributes"),
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name=_("Tenancy"),
        ),
    )

    nullable_fields = (
        "description",
        "tenant",
    )

    description = forms.CharField(
        max_length=200,
        required=False,
        label=_("Description"),
    )
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Tenant"),
    )


class ViewPrefixEditForm(forms.ModelForm):
    class Meta:
        model = Prefix

        fields = ("views",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial["views"] = self.instance.netbox_dns_views.all()
        self._permission_denied = False

        if request := current_request.get():
            if not request.user.has_perm("netbox_dns.change_view"):
                self._permission_denied = True
                self.initial["views"] = []
                self.fields["views"].disabled = True
                self.fields["views"].widget.attrs["placeholder"] = _(
                    "You do not have permission to modify assigned views"
                )

    views = DynamicModelMultipleChoiceField(
        queryset=View.objects.all(),
        required=False,
        help_text=_(
            "Explicitly assigning DNS views overrides all inherited views for this prefix"
        ),
        label=_("Assigned DNS Views"),
    )

    def clean(self, *args, **kwargs):
        if self._permission_denied:
            return

        prefix = self.instance

        super().clean(*args, **kwargs)

        views = self.cleaned_data.get("views")
        old_views = prefix.netbox_dns_views.all()

        check_views = View.objects.none()

        if not views.exists():
            if (parent := prefix.get_parents().last()) is not None:
                check_views = parent.netbox_dns_views.difference(old_views)

        else:
            check_views = views.difference(old_views)

        for view in check_views:
            try:
                for ip_address in get_ip_addresses_by_prefix(prefix, check_view=False):
                    check_dns_records(ip_address, view=view)
            except ValidationError as exc:
                self.add_error("views", exc.messages)

    def save(self, *args, **kwargs):
        prefix = self.instance

        if self._permission_denied:
            return prefix

        old_views = prefix.netbox_dns_views.all()
        views = self.cleaned_data.get("views")

        for view in views.difference(old_views):
            view.prefixes.add(prefix)
        for view in old_views.difference(views):
            view.prefixes.remove(prefix)

        return prefix
