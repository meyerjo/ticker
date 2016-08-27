import json

import datetime
import re

from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy, resolve
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from ticker.models import Club, Team, Season, League
from django.http import HttpResponseRedirect

from ticker.models import FieldAllocation
from ticker.models import PlayingField
from ticker.models import Game
from ticker.models import Match
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


def add_season(request):
    dic = request.POST
    with transaction.atomic():
        season_name = dic['season_name']
        start_date = datetime.datetime.strptime(dic['start_date'], '%d.%m.%Y')
        end_date = datetime.datetime.strptime(dic['end_date'], '%d.%m.%Y')

        if start_date > end_date:
            messages.error(request, 'Startdatum muss vor dem Enddatum liegen')
        else:
            s = Season(season_name=season_name, start_date=start_date, end_date=end_date)
            s.save()
            messages.info(request, 'Erfolgreich Saison hinzugefuegt')

    return HttpResponseRedirect(reverse('manage_season'))


def add_league(request):
    dic = request.POST
    with transaction.atomic():
        league_name = dic['league_name']
        season_id = dic['season']
        teams = request.POST.getlist('teams')
        teams = Team.objects.filter(id__in=teams)
        season = Season.objects.get(id=season_id)

        with transaction.atomic():
            l = League(associated_season=season,
                       name=league_name)
            l.save()
            l.teams.add(*teams)

            messages.info(request, 'Added new season')

    return HttpResponseRedirect(reverse('manage_league'))


def edit_league(request, league_id):
    dic = request.POST
    with transaction.atomic():
        print(request.POST)
        league_name = dic['details_league_name']
        season_id = int(dic['details_season_name'])
        league_id = int(league_id)
        team_ids = request.POST.getlist('team')
        teams = Team.objects.filter(id__in=team_ids)

        l = League.objects.get(id=league_id)
        if l.get_name() != league_name:
            l.name = league_name
        if l.associated_season.id != season_id:
            l.associated_season.id = season_id
        l.teams.remove()
        l.teams.add(*teams)
    return HttpResponseRedirect(reverse_lazy('manage_league_details', args=[league_id]))


def dynamic_matchplan(request):
    content = request.GET['dynamic_content']
    lines = content.split('\n')
    result = []
    format_1_regex = re.compile(r'^.*([0-9]{2}.[0-9]{2}.[0-9]{4} [0-9]{2}:[0-9]{2})'
                                r'\t.*\t.*\t.*\t(.*)\t-\t([^\t]*)\t*.*')

    for line in lines:
        if format_1_regex.match(line):
            matches = format_1_regex.match(line)
            tmp_dt = matches.group(1)
            tmp_d = re.match(r'[0-9]{2}.[0-9]{2}.[0-9]{4}', tmp_dt).group(0)
            tmp_t = re.match('^.*(\d{2}:\d{2}).*$', tmp_dt).group(1)
            result.append(dict(
                date=tmp_d,
                time=tmp_t,
                team_a=matches.group(2),
                team_b=matches.group(3)
            ))
    return HttpResponse(json.dumps(result))

def exists_team(request):
    def levenshteinDistance(s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    requested_name = request.GET['teamname']
    t = Team.objects.all().values_list('team_name', flat=True)

    candidates = []
    import sys
    best_dist = sys.maxsize
    best_non_threshold_candidate = None
    for tmp_name in t:
        dist = levenshteinDistance(tmp_name, requested_name)
        if dist == 0:
            return HttpResponse('OK')
        if dist <= best_dist:
            best_dist =dist
            best_non_threshold_candidate = tmp_name
        if dist <=5:
            candidates.append(tmp_name)
    if len(candidates) == 0:
        # if less than half of the words has to be rewritten
        if best_dist < len(requested_name) / 2:
            candidates.append(best_non_threshold_candidate)
            return HttpResponse('BESTFIT {0}'.format(candidates))


    if len(candidates) == 0:
        return HttpResponse('NONE')
    if len(candidates) > 1:
        return HttpResponse('MULTIPLE {0}'.format(candidates))
    return HttpResponse('OK')


def add_team_club(request):
    print(request.GET)

    team_name = request.GET['team_name']
    if Team.objects.filter(team_name=team_name).first() is not None:
        return HttpResponse('EXISTS')
    import re
    m = re.match('(.*)\d+$', team_name)
    if m:
        team_name_without_number = m.group(1).strip(' ')
    else:
        team_name_without_number = team_name
    if 'league_id' in request.GET:
        league = League.objects.filter(id=request.GET['league_id']).first()
    else:
        league = None

    c = Club.objects.filter(club_name=team_name_without_number)
    if c.exists():
        if c.count() == 1:
            c = c.first()
            # handle the case that the club exists but not the teamnaem
            with transaction.atomic():
                t = Team(team_name=team_name, parent_club=c)
                t.save()
                # add team to the league
                if league:
                    league.teams.add(t)
                return HttpResponse('OK')
        else:
            return HttpResponse('MULTIPLE CLUBS')
    else:
        with transaction.atomic():
            c = Club(club_name=team_name_without_number)
            c.save()
            t = Team(team_name=team_name, parent_club=c)
            t.save()
            if league:
                league.teams.add(t)
            return HttpResponse('OK')


def add_match(request, league_id, response_type=None):
    print(request.GET)
    date = request.GET['match_date']
    time = request.GET['match_time']
    team_a = request.GET['team_a']
    team_b = request.GET['team_b']
    submit_button = None
    response_type = None if response_type == '/' or response_type == '' else response_type

    try:
        dt = datetime.datetime.strptime('{0} {1}'.format(date, time), '%d.%m.%Y %H:%M')
    except BaseException as be:
        messages.error(request, 'Could not parse the given datetime')
        return HttpResponse('DATEFORMAT')
    team_a = Team.objects.filter(team_name=team_a).first()
    team_b = Team.objects.filter(team_name=team_b).first()
    if team_a is None or team_b is None:
        messages.error(request, 'One of the requested teams did not exist')
        return HttpResponse('TEAMEXISTENCE')
    league = League.objects.filter(id=league_id).first()
    if league is None:
        messages.error(request, 'Requested league does not eist')
        return HttpResponse('LEAGUEEXISTENCE')

    if league.teams.filter(id__in=[team_a.id, team_b.id]).count() != 2:
        messages.warning(request, 'Did not find both teams in the league.')
        return HttpResponse('LEAGUEASSOCIATION')

    print(dt, team_a.get_name(), team_b.get_name(), league.get_name())
    with transaction.atomic():
        m = Match(match_date=dt,
                  team_a=team_a,
                  team_b=team_b)
        m.save()
    return HttpResponse('OK')

def add_matches(request, league_id, response_type):
    return not_yet_implemented(request, [league_id, response_type])

def save_lineup(request, matchid, response_type):
    match = Match.objects.get(id=matchid)
    response_type = None if response_type == '/' or response_type == '' else response_type
    req_dict = request.GET
    print(req_dict)
    print(request.POST)

    data_dict = dict()
    player_game_counter = dict()
    for game in request.POST.getlist('game_id'):
        # these are the data fields expected
        data_fields = ['player_a_one_{0}'.format(game),
                       'player_a_two_{0}'.format(game),
                       'player_b_one_{0}'.format(game),
                       'player_b_two_{0}'.format(game)]
        data_dict[game] = dict(player_a=[], player_b=[])
        # iterated over all expected data fields
        for field in data_fields:
            if field in request.POST:
                tmp = request.POST[field]
                # count the amount of games
                if tmp in player_game_counter:
                    player_game_counter[tmp] += 1
                else:
                    player_game_counter[tmp] = 1
                # data dit
                if '_a_' in field:
                    data_dict[game]['player_a'].append(tmp)
                else:
                    data_dict[game]['player_b'].append(tmp)

    player_violating = []
    for player, counter in player_game_counter.items():
        print(player, counter)
        if counter > 2:
            player_violating.append(player)
    if len(player_violating) != 0:
        if response_type is None:
            p = Player.objects.filter(id__in=player_violating)
            messages.error(request, 'Players: {0} have too many games'.format(p))
            return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[matchid]))
        else:
            return HttpResponse('TOOMANYGAMES')

    player_twice_in_same_game_type = []
    gametype_player_counter = dict()
    for gameid, players in data_dict.items():
        g = Game.objects.get(id=gameid)
        if g.game_type not in gametype_player_counter:
            gametype_player_counter[g.game_type] = dict()
        for key, val in players.items():
            for v in val:
                if v in gametype_player_counter[g.game_type]:
                    gametype_player_counter[g.game_type][v] += 1
                    player_twice_in_same_game_type.append(v)
                    print(player_twice_in_same_game_type)
                else:
                    gametype_player_counter[g.game_type][v] = 1
    if len(player_twice_in_same_game_type) != 0:
        if response_type is None:
            p = Player.objects.filter(id__in=player_twice_in_same_game_type)
            messages.error(request, 'Players {0} are used twice in the same game type'.format(p))
            return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[matchid]))
        return HttpResponse('TWICE-IN-SAME-GAME-TYPE')

    with transaction.atomic():
        for gameid, players in data_dict.items():
            g = Game.objects.get(id=gameid)
            player_team_a = Player.objects.filter(id__in=players['player_a'])
            player_team_b = Player.objects.filter(id__in=players['player_b'])
            g.player_a.clear()
            g.player_a.add(*player_team_a)
            g.player_b.clear()
            g.player_b.add(*player_team_b)


    if response_type is None:
        return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[matchid]))

    return HttpResponse('OK')


def add_field(request):
    c = Club.objects.get(club_name='1. BC Beuel')
    t = Team.objects.get(team_name='1. BC Beuel 1')

    f1 = PlayingField(field_name='1. BC Beuel 1 (Feld 1)')
    f2 = PlayingField(field_name='1. BC Beuel 1 (Feld 2)')
    f1.save()
    f2.save()
    if c.fields.count() == 0:
        c.fields.add(*[f1, f2])
        t.fields.add(*(f1, f2))
        return HttpResponse('OK')
    return HttpResponse('ALREADYEXISTED')

def assign_game_to_field(request, game_id, field_id, response_type):
    response_type = None if response_type == '/' or response_type == '' else response_type
    m = Match.objects.filter(games__id=game_id).first()
    if m is None:
        return HttpResponse('MATCH NOT FOUND')

    currentallocations = FieldAllocation.objects.filter(is_active=True, field__id=field_id)
    print(currentallocations)
    with transaction.atomic():
        if currentallocations.exists():
            old_count = currentallocations.count()
            print(old_count)
            currentallocations = currentallocations.filter(game__id=game_id)
            print(currentallocations.count())

            if currentallocations.count() != old_count:
                if response_type is None:
                    messages.error(request, 'Field/Game assignment already in place')
                    return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[m.id]))
                return HttpResponse('FAIL')
        else:
            fa = FieldAllocation(field=PlayingField.objects.get(id=field_id), game=Game.objects.get(id=game_id))
            fa.save()

    if response_type is None:
        return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[m.id]))
    return HttpResponse('OK')


def remove_game_from_field(request, gameid, fieldid, response_type):
    response_type = None if response_type == '/' or response_type == '' else response_type
    game = Game.objects.get(id=gameid)
    field = PlayingField.objects.get(id=fieldid)
    m = Match.objects.filter(games__id=gameid).first()
    if m is None:
        return HttpResponse('MATCH NOT FOUND')

    fa = FieldAllocation.objects.filter(is_active=True, game=game, field=field)
    if fa.exists():
        fa.update(is_active=False, end_allocation=timezone.now())
        if response_type is None:
            return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[m.id]))
        return HttpResponse('OK')
    if response_type is None:
        messages.error(request, 'Field allocation does not exists')
        return HttpResponseRedirect(reverse_lazy('manage_ticker_interface', args=[m.id]))
    return HttpResponse('ALLOCATION NOT EXIST')


def update_score_field(request, field_id, response_type):
    """
    Updates the score for the game on the given field id. Responses either in a json fashion or with an redirect
    :param request:
    :param field_id:
    :param response_type:
    :return:
    """
    response_type = None if response_type == '/' or response_type == '' else response_type
    # get the corresponding game
    fa = FieldAllocation.objects.filter(is_active=True, field__id=field_id).order_by('-create_time').first()
    if fa is None:
        if response_type is None:
            messages.error(request, 'Could not find Field allocation for given field')
            return HttpResponseRedirect(reverse('manage_dashboard'))
        return HttpResponse('OK')
    game = fa.game
    m = Match.objects.filter(games__id=game.id).first()
    if m is None:
        if response_type is None:
            messages.error(request, 'Could not find match for the given game')
            return HttpResponseRedirect(reverse('manage_dashboard'))
        return HttpResponse('OK')

    # TODO: check if the requesting user is having the responsibility for the match

    set = game.get_current_set()
    if 'team_a' in request.POST:
        value = request.POST['team_a']
        if value == '+':
            set.add_point_team_a(m.rule)
        elif value == '-':
            set.remove_point_team_a(m.rule)
    elif 'team_b' in request.POST:
        value = request.POST['team_b']
        if value == '+':
            set.add_point_team_b(m.rule)
        elif value == '-':
            set.remove_point_team_b(m.rule)
    elif 'switch_set' in request.POST:
        if game.is_won(m.rule):
            messages.info(request, 'Game is won. Removed it from the field')
            fa = FieldAllocation.objects.filter(game=game, field__id=field_id, is_active=True)
            fa.update(
                is_active=False,
                end_allocation=timezone.now()
            )
        elif game.get_current_set().is_finished(m.rule):
            game.current_set += 1
            game.save()
        else:
            messages.error(request,'Can not switch sets at this stage')

    if response_type is None:
        return HttpResponseRedirect(reverse('manage_ticker_interface', args=[m.id]))
    return HttpResponse('OK')


def not_yet_implemented(request, *args):
    return HttpResponse('NOT YET IMPLEMENTED<br/>'
                        'RouteName: {0}<br/>'
                        'Args: {1}<br/>'.format(
        resolve(request.path_info).url_name,
        json.dumps(args)
    ))
