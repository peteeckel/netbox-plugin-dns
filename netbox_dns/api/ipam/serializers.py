from rest_framework.serializers import HyperlinkedIdentityField

from ipam.api.serializers import PrefixSerializer as IPAMPrefixSerializer

class PrefixSerializer(IPAMPrefixSerializer):
    url = HyperlinkedIdentityField(
        view_name='plugins-api:netbox_dns-api:prefix-detail'
    )

    class Meta(IPAMPrefixSerializer.Meta):
        fields = (
            'url',
            'id',
            'vrf',
            'prefix',
            'display',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.vrf is not None:
            representation['display']+=(f' [{instance.vrf.name}]')

        return representation
