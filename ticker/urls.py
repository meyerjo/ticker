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

    url('', start_page),
]