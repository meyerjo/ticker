from django import views
from django.conf.urls import url

from ticker.views.api import *

urlpatterns = [
    url(r'^club/add/?$', add_club, name='club_add'),
    url(r'^club/([0-9]+)/addteam/?$', add_team, name='team_add'),
    url(r'^club/edit/?$', edit_club, name='club_edit'),

    url(r'^field/add?$', not_yet_implemented, name='field_add'),
    url(r'^field/([0-9]+)/add/club/([0-9]+)/??$', not_yet_implemented, name='field_add_to_club'),

    url(r'^player/add/?$', add_player, name='player_add'),

    url(r'^player/parse/dynamic/?$', player_dynamic, name='player_dynamic'),

    url(r'^season/add/?$', add_season, name='add_season'),

    url(r'^season/([0-9]+)/edit/?$', not_yet_implemented, name='edit_season'),

    url(r'^league/add/?$', add_league, name='add_league'),

    url(r'^league/([0-9]+)/edit/?$', edit_league, name='edit_league'),

    url(r'^league/dynamic/matchplan/?', dynamic_matchplan, name='dynamic_matchplan')

]