from django.http import HttpResponse
from django.shortcuts import render

from ticker.models import League
from ticker.models import Match


def start_page(request):
    league = League.objects.filter(name='Bundesliga').first()
    context = dict(matches=Match.all_matches(), league=league)
    return render(request, 'index.html', context)
