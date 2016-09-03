from django.http import HttpResponse
from django.shortcuts import render

from ticker.models import League
from ticker.models import Match


def start_page(request):
    league = League.objects.filter(name='Bundesliga').first()
    matches = Match.all_matches()
    print(League.get_league_of_match(matches.first()))
    context = dict(matches=matches, league=league)
    return render(request, 'index.html', context)
