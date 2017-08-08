from django.conf.urls import url

from ticker.views.api import not_yet_implemented
from ticker.views.export import export_match, export_game
from ticker.views.match import match_ticker, match_ticker_json
from ticker.views.offline_views import offline_input, offline_score, offline_team
from ticker.views.presentation import presentation_view, score_display, team_display, display_dashboard
from ticker.views.simple_ticker import simple_ticker_interface
from ticker.views.simple_ticker import simple_ticker_login
from ticker.views.startpage import start_page
from ticker.views.user_interface import *

# /ticker/
urlpatterns = [
    url(r'^manage/clubs/?$', manage_clubs, name='manage_clubs'),

    url(r'^manage/clubs/details/([0-9]+)/?$', manage_club_details, name='manage_club_details'),

    url(r'^manage/teams/?$', not_yet_implemented, name='manage_teams'),

    url(r'^manage/teams/details/([0-9]+)/?$', manage_team_details, name='manage_teams_details'),

    url(r'^manage/players/([0-9]+)/?$', manage_players_club, name='manage_players'),
    url(r'^manage/player/([0-9]+)/edit/?$', manage_edit_player_profile, name='manage_player_profile'),

    url(r'^manage/fields/([0-9]+)/?$', manage_fields, name='manage_fields'),
    url(r'^manage/league/?$', manage_league, name='manage_league'),
    url(r'^manage/league/([0-9]+)/?$', manage_league, name='manage_league_details'),
    url(r'^manage/season/?$', manage_season, name='manage_season'),
    url(r'^manage/season/([0-9]+)/?$', manage_season, name='manage_season'),
    url(r'^manage/ticker/?$', manage_ticker, name='manage_ticker'),
    url(r'^manage/ticker/([0-9]+)/?', manage_ticker_interface, name='manage_ticker_interface'),

    url(r'^manage/game/([0-9]+)/?$', manage_game, name='manage_game'),
    url(r'^manage/ticker/simple/login/?', simple_ticker_login, name='ticker_interface_login'),
    url(r'^manage/ticker/simple/([0-9]+)/?', simple_ticker_interface, name='ticker_interface_simple'),
    url(r'^manage/?$', manage_dashboard, name='manage_dashboard'),
    url(r'^manage/presentation/?$', manage_presentation, name='manage_presentation'),
    url(r'^manage/presentation/([0-9]+)/?$', manage_presentation, name='manage_load_presentation'),
    url(r'^manage/presentation/new/?$', manage_presentation_new, name='manage_presentation_new'),
    url(r'^manage/matchdate/([0-9]+)/?$', manage_edit_matchdate, name='manage_edit_matchdate'),

    url(r'^match/([0-9]+)/?$', match_ticker, name='match_ticker'),
    url(r'^match/([0-9]+)/json/?$', match_ticker_json, name='match_ticker_json'),

    url(r'export/match/([0-9]+)/?$', export_match,  name='export_match'),
    url(r'export/game/([0-9]+)/?$', export_game,  name='export_game'),


    url(r'^presentation/([0-9]+)/match/([0-9]+)/?', presentation_view, name='presentation_view'),
    url(r'^presentation/score/field/([0-9]+)(/?|/json/?)$', score_display, name='score_display'),
    url(r'^presentation/team/field/([0-9]+)(/?|/json/?)$', team_display, name='team_display'),
    url(r'^presentation/field/dashboard/?$', display_dashboard, name='display_dashboard'),

    url(r'^settings/color/scheme/?$', manage_colors, name='manage_color_scheme'),

    url(r'^offline/input/?$', offline_input, name='offline_input'),
    url(r'^offline/score/?$', offline_score, name='offline_score'),
    url(r'^offline/team/?$', offline_team, name='offline_team'),



    url(r'^login/?$', login, name='login'),
    url('', start_page),
]
