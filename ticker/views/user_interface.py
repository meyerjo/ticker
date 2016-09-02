from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from ticker.models import Club, Team, Player, Season, League
from ticker.models import Game
from ticker.models import Match
from ticker.models import Profile


@login_required
def manage_clubs(request):
    clubs = Club.objects.all().order_by('club_name')
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs))


@login_required
def manage_club_details(request, clubid):
    clubs = Club.objects.all().order_by('club_name')
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs, details=club))


@login_required
def manage_team_details(request, teamid):
    teams = Team.objects.filter(id=int(teamid)).first()
    clubs = Club.objects.all()
    return render(request, 'user/manage_teams.html', dict(team=teams,
                                                          possible_sex=Player.possible_sex,
                                                          clubs=clubs))


@login_required
def manage_players_club(request, clubid):
    club = Club.objects.get(id=int(clubid))
    request.user.is_authenticated()
    return render(request, 'user/manage_players_club.html', dict(club=club))


@login_required
def manage_fields(request, clubid):
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_fields.html', dict(club=club))


@login_required
def manage_season(request, season_id=None):
    season = Season.objects.get(id=season_id) if season_id is not None else None
    context = dict(seasons=Season.get_seasons(), season=season)
    return render(request, 'user/manage_season.html', context)


@login_required
def manage_league(request, league_id=None):
    if league_id is not None:
        league = League.objects.get(id=league_id)
    else:
        league = None
    context = dict(leagues=League.objects.all(),
                   teams=Team.objects.all(),
                   seasons=Season.objects.filter(active=True),
                   league=league
                   )
    return render(request, 'user/manage_league.html', context)

@login_required
def manage_dashboard(request):
    context = dict()
    return render(request, 'user/manage_dashboard.html', context)

@login_required
def manage_ticker_interface(request, match_id):
    context = dict(match=Match.objects.get(id=match_id))
    return render(request, 'user/tickerinterface.html', context)

@login_required
def manage_ticker(request):
    if request.user.is_superuser:
        matches = Match.all_matches()
    else:
        p = Profile.objects.filter(user=request.user).first()
        if p is None:
            matches = []
        else:
            matches = Match.objects.filter(team_a__parent_club=p.associated_club) | \
                      Match.objects.filter(team_b__parent_club=p.associated_club)
    return render(request, 'user/manage_ticker.html', dict(matches=matches))


def simple_ticker_interface(request, game_id, randtoken):
    game = Game.objects.filter(id=game_id).first()
    return render(request, 'user/simple_ticker_interface.html', dict(game=game))


def login(request):
    from django.contrib.auth import authenticate, login
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('manage_dashboard'))

    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'user/login.html', dict())
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('manage_dashboard'))
    else:
        messages.error(request, 'Login didnot match')
        return render(request, 'user/login.html', dict())