from django import template
import json

from django.db.models import QuerySet

from ticker.models import Match

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
def is_selected(obj):
    return 'selected' if obj else ''


@register.filter
def get_date_string(obj):
    print(obj)
    return obj.strftime('%d.%m.%Y')

@register.filter
def get_players(game, args):
    match = Match.objects.get(games__id=game.id)
    split_args = args.split(',')

    team = match.team_a if split_args[1] == 'a' else match.team_b
    if split_args[1] == 'a':
        selected_player = game.player_a.all()
    else:
        selected_player = game.player_b.all()
    if len(selected_player) > 1 and game.game_type != 'mixed':
        if split_args[0] == '1':
            selected_player = selected_player[0]
        else:
            selected_player = selected_player[1]


    ret_list = []
    if 'single' in game.game_type and split_args[0] == '2':
            return []
    elif 'mixed' == game.game_type:
        players = team.get_players().filter(sex=('female' if split_args[0] == '1' else 'male'))
        for player in players:
            selected = selected_player.filter(id=player.id).exists()
            ret_list.append((player.id, player.get_name(), selected))
        return ret_list
    else:
        if isinstance(selected_player, QuerySet):
            selected_player = selected_player[0]


        if 'woman' in game.game_type or 'women' in game.game_type:
            players = team.get_players().filter(sex='female')
        else:
            players = team.get_players().filter(sex='male')

        for player in players:
            selected = selected_player.id == player.id
            ret_list.append((player.id, player.get_name(), selected))
        return ret_list

@register.filter
def is_in(str, search):
    return search in str