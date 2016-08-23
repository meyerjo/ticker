from django.conf.urls import url

from ticker.views.api import not_yet_implemented
from ticker.views.startpage import start_page
from ticker.views.user_interface import *

# /ticker/
urlpatterns = [
    url(r'^manage/clubs/?$', manage_clubs, name='manage_clubs'),

    url(r'^manage/clubs/details/([0-9]+)/?$', manage_club_details, name='manage_club_details'),

    url(r'^manage/teams/?$', not_yet_implemented, name='manage_teams'),

    url(r'^manage/teams/details/([0-9]+)/?$', manage_team_details, name='manage_teams_details'),

    url(r'^manage/players/([0-9]+)/?$', manage_players_club, name='manage_players'),

    url(r'^manage/fields/([0-9]+)/?$', manage_fields, name='manage_fields'),
    url(r'^manage/league/?$', manage_league, name='manage_league'),
    url(r'^manage/league/([0-9]+)/?$', manage_league, name='manage_league_details'),
    url(r'^manage/season/?$', manage_season, name='manage_season'),
    url(r'^manage/season/([0-9]+)/?$', manage_season, name='manage_season'),
    url(r'^manage/?$', manage_dashboard, name='manage_dashboard'),

    url('', start_page),
]