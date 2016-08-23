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


@register.filter
def player_in_team(teamobj, playerobj):
    res = teamobj.players.filter(id=playerobj.id).first()
    return 'member' if res is not None else 'nonmember'


@register.filter
def player_in_team_icon(teamobj, playerobj):
    res = teamobj.players.filter(id=playerobj.id).first()
    return '<i class="fa fa-check"></i>' if res is not None else '<i class="fa fa-ban"></i>'


@register.filter
def is_current_season_class(obj):
    return 'currentseason' if obj.season_is_on else ''


@register.filter
def get_date_string(obj):
    print(obj)
    return obj.strftime('%d.%m.%Y')