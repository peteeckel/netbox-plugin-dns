from rest_framework import mixins

from ipam.models import Prefix
from netbox.api.viewsets import BaseViewSet

from .serializers import PrefixSerializer

class PrefixViewSet(BaseViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin):
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer
