from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse

from ticker.models import Club, Team
from django.http import HttpResponseRedirect


def add_club(request):
    club, created = Club.objects.get_or_create(
        club_name=request.POST['clubname']
    )
    if created:
        messages.info(request, 'User created')
    else:
        messages.warning(request, 'Club already existed')
    return HttpResponseRedirect(reverse_lazy('manage_club_details', args=[club.id]))


def add_team(request, clubid):
    clubid = int(clubid)
    club = Club.objects.get(id=clubid)
    team_name = request.POST['team_name']
    team, created = Team.objects.get_or_create(
        parent_club=club,
        team_name=team_name
    )
    if created:
        messages.info(request, 'New Team created')
    else:
        messages.warning(request, 'Already exists')
    return HttpResponseRedirect(reverse_lazy('manage_club_details', args=[club.id]))


def edit_club(request):
    clubid = int(request.POST['clubid'])
    club = Club.objects.get(id=clubid)
    club.club_name=request.POST['clubname']
    club.save()
    return HttpResponseRedirect(reverse_lazy('manage_club_details', args=[club.id]))



def not_yet_implemented():
    return HttpResponse('not yet implemented')
