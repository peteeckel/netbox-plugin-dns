from datetime import datetime, timezone

from django import template

register = template.Library()


@register.filter(name="epoch_to_utc")
def epoch_to_utc(epoch):
    return datetime.fromtimestamp(epoch, tz=timezone.utc)
