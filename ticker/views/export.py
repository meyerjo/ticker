import re

from django.http import HttpResponse

from ticker.models import Game
from ticker.models import Match
from ticker.pdf import get_template


# noinspection PyUnusedLocal
def export_match(request, match_id):
    template_name = 'pdf/spielbericht_buli.pdf'
    match = Match.objects.filter(id=match_id).first()
    if match is None:
        return HttpResponse('ERROR')

    context = {
        b'Heim': match.team_a.get_name(),
        b'Gast': match.team_b.get_name()
    }

    mapping_names = {'1. Herreneinzel': '1HE',
                     '2. Herreneinzel': '2HE',
                     'Dameneinzel': 'DE',
                     '1. Herrendoppel': '1HD',
                     '2. Herrendoppel': '2HD',
                     'Gemischtes Doppel': 'XD',
                     'Damendoppel': 'DD'
                     }
    games = match.get_all_games()
    for game in games:
        mapped_name = mapping_names[game.name]
        if not (2 >= game.player_a.count() == game.player_b.count() <= 2):
            return HttpResponse('Error')
        player_a = game.player_a.all()
        player_b = game.player_b.all()
        tmp_heim = '{0}'.format(mapped_name)
        tmp_gast = '{0}_Gast'.format(mapped_name)
        if game.player_a.count() == 1:
            context[tmp_heim.encode('utf-8')] = player_a.first().get_name()
            context[tmp_gast.encode('utf-8')] = player_b.first().get_name()
        else:
            tmp_heim_2 = '{0}_2'.format(mapped_name)
            tmp_gast_2 = '{0}_2_Gast'.format(mapped_name)
            context[tmp_heim.encode('utf-8')] = player_a[0].get_name()
            context[tmp_heim_2.encode('utf-8')] = player_a[1].get_name()
            context[tmp_gast.encode('utf-8')] = player_b[0].get_name()
            context[tmp_gast_2.encode('utf-8')] = player_b[1].get_name()

        # set number
        for setnumber in range(1, 6):
            tmp_set = game.sets.filter(set_number=setnumber).first()
            set_home = '{0}_Satz_{1}_Heim'.format(mapped_name, setnumber)
            set_guest = '{0}_Satz_{1}_Gast'.format(mapped_name, setnumber)
            tmp_score = tmp_set.get_score()
            context[set_home.encode('utf-8')] = tmp_score[0]
            context[set_guest.encode('utf-8')] = tmp_score[1]

        # game points
        tmp_points = game.get_points()
        tmp_game_points_team_a = '{0}_Pkt_Heim'.format(mapped_name)
        tmp_game_points_team_b = '{0}_Pkt_Gast'.format(mapped_name)
        context[tmp_game_points_team_a.encode('utf-8')] = tmp_points[0]
        context[tmp_game_points_team_b.encode('utf-8')] = tmp_points[1]

        # get score
        tmp_set_points = game.get_set_score(match.rule)
        tmp_game_points_team_a = '{0}_Satz_Heim'.format(mapped_name)
        tmp_game_points_team_b = '{0}_Satz_Gast'.format(mapped_name)
        context[tmp_game_points_team_a.encode('utf-8')] = tmp_set_points[0]
        context[tmp_game_points_team_b.encode('utf-8')] = tmp_set_points[1]

        #
        result = game.is_won_by(match.rule)
        if result == 'team_a':
            tmp_score = [1, 0]
            context['{0}_Spiel_Heim'.format(mapped_name).encode('utf-8')] = tmp_score[0]
            context['{0}_Spiel_Gast'.format(mapped_name).encode('utf-8')] = tmp_score[1]
        elif result == 'team_b':
            tmp_score = [0, 1]
            context['{0}_Spiel_Heim'.format(mapped_name).encode('utf-8')] = tmp_score[0]
            context['{0}_Spiel_Gast'.format(mapped_name).encode('utf-8')] = tmp_score[1]

    #
    context[b'Pkt_Heim'] = match.get_point_score()[0]
    context[b'Pkt_Gast'] = match.get_point_score()[1]

    context[b'Satz_Heim'] = match.get_set_score()[0]
    context[b'Satz_Gast'] = match.get_set_score()[1]

    context[b'Spiel_Heim'] = match.get_score()[0]
    context[b'Spiel_Gast'] = match.get_score()[1]

    score = match.get_score()
    if score[0] + score[1] == 7:
        if score[0] > score[1]:
            context[b'Sieger'] = match.team_a.get_name()
        else:
            context[b'Sieger'] = match.team_b.get_name()

    context[b'Bundesliga'] = True
    context[b'Datum'] = match.match_time.strftime('%d.%m.%Y')
    context[b'Beginn'] = match.match_time.strftime('%H:%M')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = \
        'attachment; filename=Match_{0}.pdf'.format(match.id)

    template = get_template(template_name)
    response.write(template.render(context))
    return response


# noinspection PyUnusedLocal
def export_game(request, game_id):
    template_name = 'pdf/spielbericht_buli_spiel.pdf'
    game = Game.objects.get(id=game_id)
    match = Match.objects.filter(games__id=game.id).first()
    if match is None:
        return HttpResponse('Error')
    player_a = game.player_a.all()
    player_b = game.player_b.all()

    context = {
        b'Heim': match.team_a.get_name(),
        b'Gast': match.team_b.get_name(),
    }
    if not (2 >= player_a.count() == player_b.count() <= 2):
        return HttpResponse('Error')

    if player_a.count() == 1:
        context[b'Spieler_A_Heim'] = player_a.first().get_name()
        context[b'Spieler_A_Gast'] = player_b.first().get_name()
    elif player_b.count() == 2:
        context[b'Spieler_A_Heim'] = player_a[0].get_name()
        context[b'Spieler_B_Heim'] = player_a[1].get_name()
        context[b'Spieler_A_Gast'] = player_b[0].get_name()
        context[b'Spieler_B_Gast'] = player_b[1].get_name()

    pattern = re.compile('[\W_]+')
    game_name = pattern.sub('', game.name)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = \
        'attachment; filename=Schiedsrichterzettel_{0}_{1}.pdf'.format(game_id, game_name)

    template = get_template(template_name)
    response.write(template.render(context))
    return response
