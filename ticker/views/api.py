import json

import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http import HttpResponse

from ticker.models import Club, Team
from django.http import HttpResponseRedirect

from ticker.models import Player
from ticker.models import TeamPlayerAssociation


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


def add_player(request):
    clubid = int(request.POST['club_id'])
    teamid = int(request.POST['team_id'])
    c = Club.objects.get(id=int(clubid))
    t = Team.objects.get(id=int(teamid))
    if t.parent_club.id != c.id:
        return HttpResponse('FAIL')

    player_sex = request.POST.getlist('sex')
    player_prename = request.POST.getlist('prename')
    player_lastname = request.POST.getlist('lastname')

    if not (len(player_sex) == len(player_prename) == len(player_lastname)):
        return HttpResponse('FAIL')

    responses = []
    with transaction.atomic():
        for i, elm in enumerate(player_prename):
            prename = elm
            lastname = player_lastname[i]
            sex = player_sex[i]
            if prename == '' or lastname == '':
                continue

            # get the sex id
            sex_id = [i for i,v in enumerate(Player.possible_sex) if v[0] == sex]
            if len(sex_id) == 0:
                continue

            p, created = Player.objects.get_or_create(
                prename=prename,
                lastname=lastname,
                sex=sex
            )
            if created:
                p.save()
                t.players.add(p)
                t.save()
                now_date = datetime.date.today()
                start_date = datetime.date(year=now_date.year,
                                           month=8,
                                           day=1
                                           )
                end_date = datetime.date(year=now_date.year+1,
                                           month=7,
                                           day=31
                                           )

                team_assoc = TeamPlayerAssociation(
                    team=t,
                    player=p,
                    start_association=start_date,
                    end_association=end_date
                )
                team_assoc.save()
                responses.append('CREATED')
            else:
                responses.append('EXISTED')
    print(responses)
    if 'response_type' in request.POST:
        if request.POST['response_type'] == 'json':
            return HttpResponse(json.dumps(responses))
    return HttpResponseRedirect(reverse_lazy('manage_teams_details', args=[teamid]))


def player_dynamic(request):
    """
    Parses the dynamic content field and returns the parsed result
    :param request:
    :return:
    """
    content = request.GET['dynamic_content']
    lines = content.split('\n')
    import re
    persons = []
    sex = None
    for line in lines:
        if re.match(r'^(all_male|male|all male|herren|mann)$', line.lower()):
            sex = 'male'
            continue
        elif re.match(r'^(all_female|female|all female|damen|frau)$', line.lower()):
            sex = 'female'
            continue
        matches = re.search('([A-zäöüÄÖÜß\'\-]+),\s([A-zäöüÄÖÜß\'\-]+).*([0-9]{4}).*', line)
        matches_2 = re.search('^([A-zäöüÄÖÜß\'\-]+)\s([A-zäöüÄÖÜß\'\-]+)'
                              '\s?(male|herren|mann|female|damen|frau)?'
                              '\s?([0-9]{2}.[0-9]{2}.[0-9]{4})?$', line)
        if matches:
            tmp_sex = sex
            persons.append(dict(lastname=matches.group(1),
                                prename=matches.group(2),
                                year_of_birth=matches.group(3),
                                sex=tmp_sex))
        elif matches_2:
            tmp_sex = matches_2.group(3) if matches_2.group(3) is not None else sex

            persons.append(dict(lastname=matches_2.group(2),
                                prename=matches_2.group(1),
                                date_of_birth=matches_2.group(4),
                                sex=tmp_sex)
                           )

    return HttpResponse(json.dumps(persons))


def not_yet_implemented():
    return HttpResponse('not yet implemented')
