from django.conf.urls import url

from ticker.views.api import not_yet_implemented
from ticker.views.match import match_ticker
from ticker.views.startpage import start_page
from ticker.views.user_interface import *

# /ticker/
urlpatterns = [
    url(r'^manage/clubs/?$', manage_clubs, name='manage_clubs'),

    url(r'^manage/clubs/details/([0-9]+)/?$', manage_club_details, name='manage_club_details'),

    url(r'^manage/teams/?$', not_yet_implemented, name='manage_teams'),

    url(r'^manage/teams/details/([0-9]+)/?$', manage_team_details, name='manage_teams_details'),

    url(r'^manage/players/([0-9]+)/?$', manage_players_club, name='manage_players'),
    url(r'^manage/player/([0-9]+)/edit/?$', not_yet_implemented, name='manage_player_profile'),

    url(r'^manage/fields/([0-9]+)/?$', manage_fields, name='manage_fields'),
    url(r'^manage/league/?$', manage_league, name='manage_league'),
    url(r'^manage/league/([0-9]+)/?$', manage_league, name='manage_league_details'),
    url(r'^manage/season/?$', manage_season, name='manage_season'),
    url(r'^manage/season/([0-9]+)/?$', manage_season, name='manage_season'),
    url(r'^manage/ticker/?$', manage_ticker, name='manage_ticker'),
    url(r'^manage/ticker/([0-9]+)/?', manage_ticker_interface, name='manage_ticker_interface'),
    url(r'^manage/ticker/simple/([0-9]+)/([A-z0-9]?)/?', simple_ticker_interface, name='ticker_interface_simple'),
    url(r'^manage/?$', manage_dashboard, name='manage_dashboard'),

    url(r'^match/([0-9]+)(/?|/json/?)$', match_ticker, name='match_ticker'),
    url(r'^login/?$', login, name='login'),
    url('', start_page),
]