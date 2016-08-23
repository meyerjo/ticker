from django.shortcuts import render
from ticker.models import Club, Team, Player, Season, League


def manage_clubs(request):
    clubs = Club.objects.all().order_by('club_name')
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs))


def manage_club_details(request, clubid):
    clubs = Club.objects.all().order_by('club_name')
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_clubs.html', dict(clubs=clubs, details=club))


def manage_team_details(request, teamid):
    teams = Team.objects.filter(id=int(teamid)).first()
    return render(request, 'user/manage_teams.html', dict(team=teams, possible_sex=Player.possible_sex))


def manage_players_club(request, clubid):
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_players_club.html', dict(club=club))


def manage_fields(request, clubid):
    club = Club.objects.get(id=int(clubid))
    return render(request, 'user/manage_fields.html', dict(club=club))


def manage_season(request, season_id=None):
    season = Season.objects.get(id=season_id) if season_id is not None else None
    context = dict(seasons=Season.get_seasons(), season=season)
    return render(request, 'user/manage_season.html', context)


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


def manage_dashboard(request):
    context = dict()
    return render(request, 'user/manage_dashboard.html', context)