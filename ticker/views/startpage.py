import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.cache import cache_page

from ticker.models import League
from ticker.models import Match

from datetime import timedelta
from django.utils import timezone


@cache_page(15*60)
def start_page(request):
    league = League.objects.filter(name='Bundesliga').first()
    matches, matches_today, matches_not_today = League.league_matches_by_name('Bundesliga')

    context = dict(matches=matches_not_today, matches_today=matches_today, league=league)
    return render(request, 'index.html', context)


@cache_page(15*60)
def start_page_leagues(request, league_name):
    league = League.objects.filter(name=league_name).first()
    matches, matches_today, matches_not_today = League.league_matches_by_name(league_name)

    context = dict(matches=matches_not_today, matches_today=matches_today, league=league)
    return render(request, 'index.html', context)


@cache_page(15*60)
def start_page_leagues_json(request, league_name):
    matches, matches_today, matches_not_today = League.league_matches_by_name(league_name)
    matches_array = [dict(id=m.id, team_a=m.team_a.get_name(), team_b=m.team_b.get_name(), match_time=m.match_time.timestamp()) for m in matches]
    return HttpResponse(json.dumps(matches_array), content_type='application/json')


@cache_page(60*60)
def error_404_view(request):
    return render(request, 'error/404page.html', dict())

@cache_page(60*60)
def imprint(request):
    return render(request, 'imprint.html', dict())

def test(request):
    raise BaseException('Test')