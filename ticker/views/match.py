import jsonpickle
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ticker.models import FieldAllocation
from ticker.models import Match
from ticker.templatetags.custom_tags import format_players


def format_json(match):
    result = dict()
    result['team_a'] = match.team_a.get_name()
    result['team_b'] = match.team_b.get_name()
    result['result'] = match.get_score()

    field_allocations = FieldAllocation.objects.filter(game__match=match, is_active=True)
    result['games'] = []
    for game in match.get_all_games():
        tmp_dict_game = dict(id=game.id,
                             name=game.name,
                             player_a=format_players(game.player_a),
                             player_b=format_players(game.player_b))
        tmp_dict_game['sets'] = []
        for set in game.get_set_objects():
            tmp_dict_game['sets'].append(
                [set.id, set.set_number, set.get_score()]
            )
        alloc = field_allocations.filter(game=game).first()
        if alloc is None:
            tmp_dict_game['field'] = -1
        else:
            tmp_dict_game['field'] = alloc.field.id

        result['games'].append(tmp_dict_game)
        result['current_set'] = game.get_current_set()
    return result


@cache_page(5*60)
def match_ticker(request, matchid):
    m = Match.objects.filter(id=matchid).first()
    return render(request, 'match.html', dict(match=m))


@cache_page(10)
def match_ticker_json(request, matchid):
    m = Match.objects.filter(id=matchid).first()
    return HttpResponse(jsonpickle.encode(format_json(m)), content_type='application/json')
