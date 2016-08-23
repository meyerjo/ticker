from django.shortcuts import render
from ticker.models import Club, Team, Player


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


def manage_season(request):
    context = dict()
    return render(request, 'user/manage_season.html', context)


def manage_league(request):
    context = dict()
    return render(request, 'user/manage_league.html', context)