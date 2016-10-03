

# TODO: remove this should only stay as quickfix
from django.http import HttpResponse
from django.shortcuts import render


def offline_input(request):
    return render(request, 'user/simple_ticker_interface_offline.html', dict())


def offline_score(request):
    return render(request, 'presentation/score_display_offline.html', dict())


def offline_team(request):
    return render(request, 'presentation/team_display_offline.html', dict())


def offline_appcache(request):
    output = "CACHE MANIFEST\n"
    output += "/ticker/offline/input\n"
    output += "/ticker/offline/team\n"
    output += "/ticker/offline/score\n"
    output += "/static/css/ticker_interface_simple.css\n"
    output += "/static/ext/bootstrap/dist/css/bootstrap.min.css\n"
    output += "/static/ext/bootstrap/dist/css/bootstrap-theme.min.css\n"
    output += "/static/ext/bootstrap/dist/css/bootstrap-theme.min.css\n"
    output += "//code.jquery.com/jquery-3.1.0.min.js\n"

    return HttpResponse(output, content_type='text/plain')
