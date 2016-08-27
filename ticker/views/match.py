from django.http import HttpResponse
from django.shortcuts import render

from ticker.models import Match


def match_ticker(request, matchid, response_type):
    print(matchid)
    print(response_type)

    m = Match.objects.filter(id=matchid).first()

    return render(request, 'match.html', dict(match=m))