from django import template
import json


register = template.Library()


@register.filter
def check_if_in_responsible_profiles(obj, user):
    if obj is None:
        return False
    if user is None:
        return False
    if user.is_superuser:
        return True
    for elm in obj:
        if elm.user.id == user.id:
            return True
    return False