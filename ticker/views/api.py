import json

import datetime
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse, reverse_lazy, resolve
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from ticker.models import Club, Team, Season, League, Rules
from django.http import HttpResponseRedirect

from ticker.models import ColorDefinition
from ticker.models import DefinableColor
from ticker.models import FieldAllocation
from ticker.models import PlayingField
from ticker.models import Game
from ticker.models import Match
from ticker.models import Player
from ticker.models import PresentationToken
from ticker.models import Profile
from ticker.models import TeamPlayerAssociation

@login_required
@permission_required('ticker.add_club')
def add_club(request):
    club, created = Club.objects.get_or_create(
        club_name=request.POST['clubname']
    )
    if created:
        messages.info(request, 'User created')
    else:
        messages.warning(request, 'Club already existed')
    return HttpResponseRedirect(reverse_lazy('manage_club_details', args=[club.id]))

@login_required
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

@login_required
def edit_club(request):
    clubid = int(request.POST['clubid'])
    club = Club.objects.get(id=clubid)
    club.club_name=request.POST['clubname']
    club.save()
    return HttpResponseRedirect(reverse_lazy('manage_club_details', args=[club.id]))

@login_required
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
                start_date = datetime.date(year=now_date.year, month=8, day=1)
                end_date = datetime.date(year=now_date.year+1, month=7, day=31)

                team_assoc = TeamPlayerAssociation(team=t, player=p, start_association=start_date,
                                                   end_association=end_date)
                team_assoc.save()
                responses.append('CREATED')
            else:
                responses.append('EXISTED')
    print(responses)
    if 'response_type' in request.POST:
        if request.POST['response_type'] == 'json':
            return HttpResponse(json.dumps(responses))
    return HttpResponseRedirect(reverse_lazy('manage_teams_details', args=[teamid]))

@login_required
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

@login_required
@permission_required('ticker.add_season')
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


@login_required
@permission_required('ticker.add_league')
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


@login_required
@permission_required('ticker.edit_league')
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


@login_required
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

@login_required
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


@login_required
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


@login_required
def add_match(request, league_id, response_type=None):
    print(request.GET)
    date = request.GET.getlist('match_date')
    time = request.GET.getlist('match_time')
    team_a = request.GET.getlist('team_a')
    team_b = request.GET.getlist('team_b')
    submit_button = None
    response_type = None if response_type == '/' or response_type == '' else response_type

    json_responses = []
    for i, match_time in enumerate(time):
        if match_time == '':
            continue

        date_str = '{0} {1}'.format(date[i], time[i])
        try:
            dt = datetime.datetime.strptime(date_str, '%d.%m.%Y %H:%M')
        except BaseException as be:
            if response_type is None:
                messages.error(request, 'Could not parse the given datetime')
            else:
                json_responses.append(
                    'DATEFORMAT-ERROR: {0}'.format(date_str)
                )
            continue

        tmp_team_a = Team.objects.filter(team_name=team_a[i]).first()
        tmp_team_b = Team.objects.filter(team_name=team_b[i]).first()
        if tmp_team_a is None or tmp_team_b is None:
            if response_type is None:
                messages.error(request, 'One of the requested teams did not exist')
            else:
                json_responses.append(
                    'TEAMEXISTENCE {0}:{1}, {2}:{3}'.format(
                        tmp_team_a, tmp_team_a is not None,
                        tmp_team_b, tmp_team_b is not None
                    )
                )
            continue

        league = League.objects.filter(id=league_id).first()
        if league is None:
            if response_type is None:
                messages.error(request, 'Requested league does not exist')
            else:
                json_responses.append('LEAGUEEXISTENCE')
            continue

        if league.teams.filter(id__in=[tmp_team_a.id, tmp_team_b.id]).count() != 2:
            if response_type is None:
                messages.warning(request, 'Did not find both teams in the league.')
            else:
                json_responses.append('TEAM NOT IN LEAGUE')
            continue

        rules = Rules.objects.all().first()
        print(dt, tmp_team_a.get_name(), tmp_team_b.get_name(), league.get_name())
        with transaction.atomic():
            m = Match(match_time=dt,
                      team_a=tmp_team_a,
                      team_b=tmp_team_b,
                      rule=rules)
            m.save()
            league.matches.add(m)
        json_responses.append('OK')

    if response_type is not None:
        return HttpResponse(json.dumps(json_responses))
    return HttpResponseRedirect(reverse_lazy('manage_league_details', args=[league_id]))


@login_required
def add_matches(request, league_id, response_type):
    return not_yet_implemented(request, [league_id, response_type])


@login_required
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

@login_required
def add_field(request):
    return HttpResponse('implement this')
    # TODO Implement this properly
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


@login_required
@permission_required('ticker.add_fieldallocation')
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


@login_required
@permission_required('ticker.change_fieldallocation')
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


@login_required
@permission_required('ticker.add_point')
@permission_required('ticker.change_point')
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
        return HttpResponse('FAIL-MISSING FIELD ALLOCATION')
    game = fa.game
    m = Match.objects.filter(games__id=game.id).first()
    if m is None:
        if response_type is None:
            messages.error(request, 'Could not find match for the given game')
            return HttpResponseRedirect(reverse('manage_dashboard'))
        return HttpResponse('FAIL-UNKNOWN MATCH')

    # TODO: check if the requesting user is having the responsibility for the match
    updated_information = dict()
    set = game.get_current_set()
    if 'team_a' in request.POST:
        value = request.POST['team_a']
        if value == '+':
            set.add_point_team_a(m.rule)
        elif value == '-':
            set.remove_point_team_a(m.rule)
        updated_information['type'] = 'score-update'
        updated_information['game_id'] = game.id
        updated_information['set_id'] = set.id
        updated_information['field_id'] = field_id
        updated_information['set_number'] = set.set_number
        updated_information['set_score'] = set.get_score()
        updated_information['game_score'] = game.get_sets()
        updated_information['set_finished'] = set.is_finished(m.rule)
    elif 'team_b' in request.POST:
        value = request.POST['team_b']
        if value == '+':
            set.add_point_team_b(m.rule)
        elif value == '-':
            set.remove_point_team_b(m.rule)
        updated_information['type'] = 'score-update'
        updated_information['game_id'] = game.id
        updated_information['set_id'] = set.id
        updated_information['field_id'] = field_id
        updated_information['set_number'] = set.set_number
        updated_information['set_score'] = set.get_score()
        updated_information['game_score'] = game.get_sets()
        updated_information['set_finished'] = set.is_finished(m.rule)
    elif 'switch_set' in request.POST:
        if game.is_won(m.rule):
            messages.info(request, 'Game is won. Removed it from the field')
            fa = FieldAllocation.objects.filter(game=game, field__id=field_id, is_active=True)
            fa.update(
                is_active=False,
                end_allocation=timezone.now()
            )
            updated_information['type'] = 'clear-field'
            updated_information['field_id'] = field_id
            updated_information['game_field_link'] = str(reverse_lazy('remove_game_to_field', args=[game.id, field_id, '/']))
            updated_information['game_name'] = game.name
            updated_information['game_id'] = game.id
        elif game.get_current_set().is_finished(m.rule):
            game.current_set += 1
            game.save()

            set = game.get_current_set()
            updated_information['type'] = 'update-current-set'
            updated_information['field_id'] = field_id
            updated_information['set_number'] = game.current_set
            updated_information['set_label'] = 'Satz {0}'.format(set.set_number)
            updated_information['set_score'] = set.get_score()
        else:
            if response_type is None:
                messages.error(request,'Can not switch sets at this stage')
            updated_information = dict(error='Cannot switch sets at this stage')
    if 'error' not in updated_information:
        updated_information['error'] = None

    print(updated_information)

    if response_type is None:
        return HttpResponseRedirect(reverse('manage_ticker_interface', args=[m.id]))
    return HttpResponse(json.dumps(updated_information))


@login_required
def edit_parent_club(request, team_id):
    old_parent_club = request.POST['old_parent_club']
    new_club_id = request.POST['parent_club']

    team = Team.objects.get(id=team_id)
    profile = Profile.objects.filter(user=request.user).first()
    if profile is None and not request.user.is_superuser:
        messages.error(request, 'Your account is not associated to any club')
        return HttpResponseRedirect(reverse_lazy('manage_team_details', args=[team_id]))
    if profile.associated_club.id != team.parent_club.id and not request.user.is_superuser:
        messages.error(request, 'Your account is not associated to this club')
        return HttpResponseRedirect(reverse_lazy('manage_team_details', args=[team_id]))

    # change team
    team.parent_club = Club.objects.filter(id=new_club_id).first()
    team.save()

    return HttpResponseRedirect(reverse_lazy('manage_teams_details', args=[team_id]))


def not_yet_implemented(request, *args):
    return HttpResponse('NOT YET IMPLEMENTED<br/>'
                        'RouteName: {0}<br/>'
                        'Args: {1}<br/>'.format(
        resolve(request.path_info).url_name,
        json.dumps(args)
    ))


def validate_token(request):
    submitted_token = request.POST['token']

    token = PresentationToken.objects.filter(
        token=submitted_token,
    ).first()
    if token is None:
        messages.error(request, 'Invalid Token')
        return HttpResponseRedirect(reverse('ticker_interface_login'))

    if token.is_used:
        messages.error(request, 'Token is outdated')
        return HttpResponseRedirect(reverse('ticker_interface_login'))
    request.session['token'] = submitted_token
    return HttpResponseRedirect(reverse('ticker_interface_simple', args=[token.field.id]))


@login_required()
def api_new_token(request, field_id):
    pf = PlayingField.objects.filter(id=field_id).first()
    # TODO: validate if the user has permission to generate a token for this match
    current_tokens = PresentationToken.objects.filter(
        field_id=field_id,
        is_used=False
    ).first()
    if current_tokens is not None:
        print(current_tokens.token)
        messages.error(request, 'Another token already exists')
        return redirect(request.META.get('HTTP_REFERER'))
    with transaction.atomic():
        import time, hashlib
        t_str = str(time.time())
        t_str = hashlib.md5(t_str.encode('utf-8')).hexdigest().upper()[:6]
        token = PresentationToken(field=pf, user=request.user, token=t_str)
        token.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def invalidate_token(request, token_id):
    t = PresentationToken.objects.get(id=token_id)

    if request.user.is_superuser or t.user == request.user:
        t.is_used = True
        t.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def api_change_color(request):
    p = Profile.objects.filter(user=request.user).first()
    if p is None:
        return HttpResponseRedirect(reverse('manage_color_scheme'))
    definable_colors = DefinableColor.objects.all()
    club = p.associated_club
    for color in definable_colors:
        print(request.POST)
        if 'colorcode_{0}'.format(color.id) not in request.POST:
            continue

        tmp_color = request.POST['colorcode_{0}'.format(color.id)]

        definition = ColorDefinition.objects.filter(club=club, color_definition=color).first()
        if definition is None:
            cd = ColorDefinition(club=club, color_definition=color, color_hexcode=tmp_color)
            cd.save()
        else:
            definition.color_hexcode = tmp_color
            definition.save()

    return HttpResponseRedirect(reverse('manage_color_scheme'))

