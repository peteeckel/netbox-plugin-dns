from utilities.forms.fields import DynamicModelMultipleChoiceField
from utilities.forms.widgets import APISelectMultiple


__all__ = ("PrefixDynamicModelMultipleChoiceField",)


class PrefixDynamicModelMultipleChoiceField(DynamicModelMultipleChoiceField):
    widget = APISelectMultiple(api_url="/api/plugins/netbox-dns/prefixes")

    def label_from_instance(self, obj):
        if obj.vrf:
            return f"{str(obj.prefix)} [{obj.vrf.name}]"

        return str(obj.prefix)
