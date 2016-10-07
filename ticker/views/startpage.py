from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.cache import cache_page

from ticker.models import League
from ticker.models import Match


@cache_page(15*60)
def start_page(request):
    league = League.objects.filter(name='Bundesliga').first()
    from datetime import timedelta
    from django.utils import timezone
    last_week = timezone.now() - timedelta(days=7)
    matches = Match.objects.filter(match_time__gte=last_week)
    context = dict(matches=matches, league=league)
    return render(request, 'index.html', context)


@cache_page(60*60)
def error_404_view(request):
    return render(request, 'error/404page.html', dict())
