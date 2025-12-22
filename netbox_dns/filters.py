from django_filters import NumberFilter

from netbox_dns.fields import TimePeriodField


class TimePeriodFilter(NumberFilter):
    field_class = TimePeriodField
