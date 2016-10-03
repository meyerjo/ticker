import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import cache_page

from ticker.models import Club
from ticker.models import FieldAllocation
from ticker.models import Match
from ticker.models import PlayingField
from ticker.models import Team
from ticker.models.presentation import Presentation, PresentationSlideTeam
from ticker.templatetags.custom_tags import format_players


@cache_page(15*60)
def display_dashboard(request):
    clubs = Club.objects.all().order_by('club_name')
    return render(request, 'presentation/score_dashboard.html', dict(clubs=clubs))


def score_display(request, field_id, response_type):
    fa = FieldAllocation.objects.filter(field_id=field_id, is_active=True).first()
    game = fa.game if fa else None
    response_type = None if response_type == '/' or response_type == '' else response_type
    if response_type is not None:
        resp = {
            1: [0, 0],
            2: [0, 0],
            3: [0, 0],
            4: [0, 0],
            5: [0, 0],
            'active_set': 1
        }
        if game is None:
            return HttpResponse(json.dumps(resp), content_type='application/json')

        for set in game.sets.all():
            resp[set.set_number] = set.get_score()
        resp['active_set'] = game.current_set
        return HttpResponse(json.dumps(resp), content_type='application/json')

    team_a = Team.objects.filter(fields__id=field_id).first()
    return render(request, 'presentation/score_display.html', dict(game=game, field_id=field_id, team_a=team_a))


def team_display(request, field_id, response_type):
    fa = FieldAllocation.objects.filter(field_id=field_id, is_active=True).first()
    game = fa.game if fa else None
    response_type = None if response_type == '/' or response_type == '' else response_type
    if response_type is not None:
        resp = dict(team_a='', team_b='')
        if game is None:
            return HttpResponse(json.dumps(resp), content_type='application/json')
        resp['team_a'] = format_players(game.player_a.all())
        resp['team_b'] = format_players(game.player_b.all())
        return HttpResponse(json.dumps(resp), content_type='application/json')

    team_a = Team.objects.filter(fields__id=field_id).first()
    return render(request, 'presentation/team_display.html', dict(game=game, field_id=field_id, team_a=team_a))


def presentation_view(request, presentation_id, match_id):
    # TODO: Implement this
    match = Match.objects.get(id=match_id)
    # fields = FieldAllocation.objects.filter(is_active=True, game__in=match.games)
    team_fields = PlayingField.objects.filter(team=match.team_a)

    team_a = match.team_a
    # presentation = Presentation.objects.filter(team=team_a).first()
    # slides = PresentationSlideTeam.objects.filter(presentation=presentation).\
    #    order_by('slide_number').values_list('slide', flat=True)
    slides = []
    next_home_games = Match.objects.filter(match_time__gte=timezone.now(),
                                           team_a=match.team_a)
    return render(request, 'presentation/general_presentation_reveal.html', dict(slides=slides,
                                                                                 match=match,
                                                                                 fields=team_fields,
                                                                                 next_home_games=next_home_games))