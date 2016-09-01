import json

from django.http import HttpResponse
from django.shortcuts import render

from ticker.models import Club
from ticker.models import FieldAllocation
from ticker.models import Match
from ticker.templatetags.custom_tags import format_players


def presentation_view(request, presentation_id, match_id):
    m = Match.objects.get(id=match_id)
    #    p = Presentation.objects.get
    return render(request, 'presentation/general_presentation.html', dict(match=m))


def display_dashboard(request):
    clubs = Club.objects.all().order_by('club_name')

    return render(request, 'presentation/score_dashboard.html', dict(clubs=clubs))


def score_display(request, field_id, response_type):
    fa = FieldAllocation.objects.filter(field_id=field_id, is_active=True).first()
    game = fa.game if fa else None
    print(response_type)
    response_type = None if response_type == '/' or response_type=='' else response_type
    if response_type is not None:
        resp = {
                   1: [0,0],
                   2: [0,0],
                   3: [0,0],
                   4: [0,0],
                   5: [0,0]
        }
        if game is None:
            return HttpResponse(json.dumps(resp))

        for set in game.sets.all():
            resp[set.set_number] = set.get_score()
        return HttpResponse(json.dumps(resp))

    return render(request, 'presentation/score_display.html', dict(game=game, field_id=field_id))


def team_display(request, field_id, response_type):
    fa = FieldAllocation.objects.filter(field_id=field_id, is_active=True).first()
    game = fa.game if fa else None
    response_type = None if response_type == '/' or response_type == '' else response_type
    if response_type is not None:
        resp = dict(team_a='', team_b='')
        if game is None:
            return HttpResponse(json.dumps(resp))
        resp['team_a'] = format_players(game.player_a.all())
        resp['team_b'] = format_players(game.player_b.all())
        return HttpResponse(json.dumps(resp))

    return render(request, 'presentation/team_display.html', dict(game=game, field_id=field_id))