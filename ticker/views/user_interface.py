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
