from rest_framework.serializers import HyperlinkedIdentityField

from ipam.api.serializers import PrefixSerializer as IPAMPrefixSerializer


__all__ = ("PrefixSerializer",)


class PrefixSerializer(IPAMPrefixSerializer):
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_dns-api:prefix-detail")

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.vrf is not None:
            representation["display"] += f" [{instance.vrf.name}]"

        return representation
