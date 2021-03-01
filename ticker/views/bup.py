import errno
import io
import json
import os
import os.path
import re
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from ticker.models import (
    FieldAllocation,
    Game,
    League,
    Match,
    Player,
    PlayingField,
    Season,
    TeamPlayerAssociation,
)

LOCAL_BUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'bup'))
VALID_VERSION = re.compile(r'^[0-9]+\.[0-9]{1,2}\.[0-9]{1,2}\.[0-9A-Za-z.]+|dev$')


@login_required
def manage_bup_overview(request):
    note = request.GET.get('note')

    try:
        cur = os.readlink(os.path.join(LOCAL_BUP_DIR, 'cur'))
    except OSError as ose:
        if ose.errno == errno.ENOENT:
            cur = None

    return render(request, 'bup/manage.html', {
        'note': note,
        'versions': [v for v in os.listdir(LOCAL_BUP_DIR) if VALID_VERSION.match(v)],
        'cur': cur,
    })


@require_POST
@login_required
def manage_bup_switch(request):
    new_v = request.POST.get('v', '')
    if not VALID_VERSION.match(new_v):
        return HttpResponseBadRequest()

    # Cannot use tempfile since that always creates a new file/directory.
    # We want a symlink instead.
    # Fortunately, it's fine if we race the same version
    tmp_fn = os.path.join(LOCAL_BUP_DIR, 'tmp_cur_symlink_%s' % new_v)
    try:
        os.symlink(new_v, tmp_fn, target_is_directory=True)
    except OSError as ose:
        return HttpResponseServerError('Can symlink nicht erstellen: %s' % ose.strerror)

    cur_fn = os.path.join(LOCAL_BUP_DIR, 'cur')
    try:
        os.rename(tmp_fn, cur_fn)
    except OSError as ose:
        return HttpResponseServerError('Can symlink nicht erstellen: %s' % ose.strerror)

    return HttpResponseRedirect(
        reverse('manage_bup_overview') + '?' +
        urllib.parse.urlencode({'note': 'Aktuelles Badminton Umpire Panel ist %s' % new_v}))


@require_POST
@login_required
def manage_bup_download(request):
    DOWNLOAD_URL = 'https://aufschlagwechsel.de/bup.zip'

    try:
        with urllib.request.urlopen(DOWNLOAD_URL) as req:
            zip_contents = req.read()
    except urllib.error.URLError as ue:
        return HttpResponseServerError('Aktualisierung fehlgeschlagen: %s' % ue.reason)

    with zipfile.ZipFile(io.BytesIO(zip_contents), 'r') as zf:
        with zf.open('bup/VERSION', 'r') as version_f:
            version = version_f.read().decode('utf-8').strip()

        target_dn = os.path.join(LOCAL_BUP_DIR, version)
        if os.path.exists(target_dn):
            return HttpResponseRedirect(
                reverse('manage_bup_overview') + '?' +
                urllib.parse.urlencode({'note': 'Badminton Umpire Panel v%s ist bereits installiert.' % version}))

        try:
            tmp_dn = tempfile.mkdtemp(prefix='tmp_', suffix='.extracting', dir=LOCAL_BUP_DIR)
        except OSError as ose:
            return HttpResponseServerError('%s (keine Schreibrechte auf %s?)' % (ose.strerror, LOCAL_BUP_DIR))

        try:
            for name in zf.namelist():
                assert name.startswith('bup/')
                target_fn = os.path.abspath(os.path.join(tmp_dn, name[len('bup/'):]))
                if not target_fn.startswith(tmp_dn):
                    raise Exception('Path traversal: %s' % target_fn)

                if name.endswith('/'):
                    if not os.path.exists(target_fn):
                        os.mkdir(target_fn)
                else:
                    with zf.open(name, 'r') as inf, open(target_fn, 'wb') as outf:
                        shutil.copyfileobj(inf, outf)
        except:
            assert '/bup' in tmp_dn
            shutil.rmtree(tmp_dn)
            raise

    try:
        assert not os.path.exists(target_dn)
        os.rename(tmp_dn, target_dn)
    except OSError as ose:
        assert '/bup' in tmp_dn
        shutil.rmtree(tmp_dn)
        if os.path.exists(target_dn):
            return HttpResponseRedirect(
                reverse('manage_bup_overview') + '?' +
                urllib.parse.urlencode({'note': 'Badminton Umpire Panel v%s wurde parallel installiert!' % version}))
        else:
            raise

    return HttpResponseRedirect(
        reverse('manage_bup_overview') + '?' +
        urllib.parse.urlencode({'note': 'Badminton Umpire Panel v%s installiert.' % version}))


def _calc_match(m):
    setup = {
        'match_name': m.name,
        'match_id': 'jticker_m%s' % m.id,
        'jticker_match_id': m.id,
    }

    player_a = m.player_a.all()
    player_b = m.player_b.all()
    setup['is_doubles'] = m.game_type not in ('single', 'womansingle')
    setup['teams'] = [{
        'players': [{
            'name': p.get_name(),
        } for p in players],
    } for players in (player_a, player_b)]

    games = m.sets.order_by('set_number').all()
    netscore = []
    for g in games:
        score = g.get_score()
        if score != [0, 0]:
            netscore.append(score)

    res = {
        'network_score': netscore,
        'setup': setup,
    }

    if m.presses_json is not None:
        res['presses_json'] = m.presses_json

    return res


def _get_players(players):
    return [{
        'firstname': p.prename,
        'lastname': p.lastname,
        'name': p.get_name(),
        'gender': 'm' if p.sex == 'male' else 'f',
    } for p in players]


@login_required
def bup_list(request):
    tm_id = request.GET['id']
    assert re.match(r'^[0-9]+$', tm_id)

    tm = Match.objects.filter(id=tm_id).first()
    if tm is None:
        raise Http404('team match %s not found!' % tm_id)
    league = League.objects.filter(matches__in=[tm]).first()

    team_names = [tm.team_a.get_name(), tm.team_b.get_name()]
    match_objs = tm.get_all_games()
    matches = list(map(_calc_match, match_objs))

    match_ids = [m.id for m in match_objs]
    fas = FieldAllocation.objects.filter(game_id__in=match_ids, is_active=True).all()
    COURT_COUNT = 2
    courts = [{
        'court_id': court_id,
    } for court_id in range(1, COURT_COUNT + 1)]
    for fa in fas:
        assert fa.field_id >= 1
        courts[fa.field_id - 1]['match_id'] = 'jticker_m%s' % fa.game_id

    res = {
        'status': 'ok',
        'id': 'jticker_' + tm_id,
        'team_competition': True,
        'team_names': team_names,
        'matches': matches,
        'courts': courts,
        'league_key': league.league_key,
    }

    if request.GET.get('all'):
        res['all_players'] = [_get_players(tm.player_a.all()), _get_players(tm.player_a.all())]

    return HttpResponse(json.dumps(res), content_type='application/json')


def _select_players(season, team, available, playerspec_list):
    assert isinstance(playerspec_list, list)

    res = []
    for pspec in playerspec_list:
        firstname = pspec['firstname']
        assert firstname
        lastname = pspec['lastname']
        assert lastname
        assert pspec['gender']
        sex = 'male' if pspec['gender'] == 'm' else 'female'

        for a in available:
            if (a.prename == firstname) and (a.lastname == lastname):
                res.append(a)
                break
        else:
            # Player at another team / club?
            p = Player.objects.filter(prename=firstname, lastname=lastname, sex=sex).first()
            if p is None:  # New player
                p = Player.objects.create(prename=firstname, lastname=lastname, sex=sex)
                p.save()
            res.append(p)

            team.players.add(p)
            team.save()

            team_assoc = TeamPlayerAssociation(
                team=team, player=p,
                start_association=season.start_date,
                end_association=season.end_date)
            team_assoc.save()

    return res


@login_required
def bup_teamsetup(request):
    import logging
    logger = logging.getLogger(__name__)
    tm_id = request.GET['tm_id']
    assert re.match(r'^[0-9]+$', tm_id), 'tm_id does not pass regex'
    try:
        teamsetup = json.loads(request.POST['players_json'])
        with transaction.atomic():
            season = Season.get_current_season()

            tm = Match.objects.filter(id=tm_id).first()
            if tm is None:
                raise Http404('teammatch %s not found!' % tm_id)

            available_players = [tm.team_a.get_players(), tm.team_a.get_players()]

            for m in tm.get_all_games():
                ts = teamsetup[str(m.id)]
                assert len(ts) == 2
                m.player_a.set(_select_players(season, tm.team_a, available_players[0], ts[0]))
                m.player_b.set(_select_players(season, tm.team_b, available_players[1], ts[1]))
                m.save()
    except BaseException as e:
        print(str(e))
        logger.error(str(e))
        raise e
    return HttpResponse(json.dumps({
        'status': 'ok',
    }), content_type='application/json')


@login_required
def bup_sync(request):
    match_id = request.GET['match_id']
    assert re.match(r'^[0-9]+$', match_id)

    new_scores = json.loads(request.POST['score_json'])
    assert all(isinstance(a, int) and isinstance(b, int) for a, b in new_scores)

    with transaction.atomic():
        match = Game.objects.filter(id=match_id).first()
        if match is None:
            raise Http404('match %s not found!' % match_id)

        court_id = int(request.POST['court_id'])
        fa = FieldAllocation.objects.filter(is_active=True, field__id=court_id).first()
        newfa_required = False
        if fa:
            if fa.game_id != match_id:
                fa.end_allocation = timezone.now()
                fa.is_active = False
                fa.save()
                newfa_required = True
        else:
            newfa_required = True
        if newfa_required:
            newfa = FieldAllocation(field=PlayingField.objects.get(id=court_id), game=match)
            newfa.save()

        new_len = len(new_scores)
        if new_len != match.current_set:
            match.current_set = new_len
        assert isinstance(request.POST['presses_json'], str)
        match.presses_json = request.POST['presses_json']
        match.save()

        rule = match.get_match().rule
        games = match.sets.order_by('set_number').all()
        for cur_game in games:
            cur_a, cur_b = cur_game.get_score()
            idx = cur_game.set_number - 1
            new_a, new_b = new_scores[idx] if idx < len(new_scores) else [0, 0]
            diff_a = new_a - cur_a
            diff_b = new_b - cur_b

            if not rule.validate(new_a, new_b):
                continue

            while diff_a > 0:
                cur_game.add_point_team_a(rule)
                diff_a -= 1
            while diff_a < 0:
                cur_game.remove_point_team_a(rule)
                diff_a += 1
            while diff_b > 0:
                cur_game.add_point_team_b(rule)
                diff_b -= 1
            while diff_b < 0:
                cur_game.remove_point_team_b(rule)
                diff_b += 1

    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
