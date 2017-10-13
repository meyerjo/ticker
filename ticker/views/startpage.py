import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ticker.models import League, Season


@cache_page(5*60)
def start_page(request):
    league_name = 'Bundesliga'
    current_season = Season.get_current_season()
    league = League.objects.filter(name=league_name, associated_season=current_season).first()
    matches, matches_today, matches_not_today = League.league_matches_by_name(league_name)
    other_leagues = League.get_other_leagues(league)

    context = dict(matches=matches_not_today, matches_today=matches_today, league=league, other_leagues=other_leagues)
    return render(request, 'index.html', context)


@cache_page(15*60)
def start_page_leagues(request, league_name):
    current_season = Season.get_current_season()
    league = League.objects.filter(name=league_name, associated_season=current_season).first()
    matches, matches_today, matches_not_today = League.league_matches_by_name(league_name)
    other_leagues = League.get_other_leagues(league)

    context = dict(matches=matches_not_today, matches_today=matches_today, league=league, other_leagues=other_leagues)
    return render(request, 'index.html', context)


@cache_page(15*60)
def start_page_leagues_json(request, league_name):
    matches, matches_today, matches_not_today = League.league_matches_by_name(league_name)
    if matches is None:
        matches_array = []
    else:
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