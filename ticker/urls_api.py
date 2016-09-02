from django import views
from django.conf.urls import url

from ticker.views.api import *

urlpatterns = [
    url(r'^club/add/?$', add_club, name='club_add'),
    url(r'^club/([0-9]+)/addteam/?$', add_team, name='team_add'),
    url(r'^team/exists/?$', exists_team, name='exists_team' ),
    url(r'^team/add/json/?', add_team_club, name='add_team_club_json'),
    url(r'^team/edit/parentclub/([0-9]+)/?$', edit_parent_club, name='edit_parent_club' ),
    url(r'^club/edit/?$', edit_club, name='club_edit'),

    url(r'^field/test/$', add_field, name='fields_add'),
    url(r'^field/add?$', not_yet_implemented, name='field_add'),
    url(r'^field/([0-9]+)/add/club/([0-9]+)/??$', not_yet_implemented, name='field_add_to_club'),

    url(r'^player/add/?$', add_player, name='player_add'),

    url(r'^player/parse/dynamic/?$', player_dynamic, name='player_dynamic'),

    url(r'^season/add/?$', add_season, name='add_season'),

    url(r'^season/([0-9]+)/edit/?$', not_yet_implemented, name='edit_season'),

    url(r'^league/add/?$', add_league, name='add_league'),

    url(r'^league/([0-9]+)/edit/?$', edit_league, name='edit_league'),

    url(r'^league/dynamic/matchplan/?', dynamic_matchplan, name='dynamic_matchplan'),

    url(r'^league/([0-9]+)/match/add(/?|/json)$', add_match, name='add_match_league' ),
    url(r'^league/([0-9]+)/matches/add(/?|/json)$', add_matches, name='add_matches_league' ),

    url(r'^match/([0-9]+)/lineup/save(/?|/json/?)$', save_lineup, name='match_lineup_save'),
    url(r'^match/assign/game/([0-9]+)/to/field/([0-9]+)(/?|/json/?)$', assign_game_to_field, name='assign_game_to_field'),
    url(r'^match/remove/game/([0-9]+)/from/field/([0-9]+)(/?|/json/?)$', remove_game_from_field, name='remove_game_to_field'),
    url(r'^match/ticker/simple/new/token/([0-9]+)?$', api_new_token, name='api_new_token'),
    url(r'^match/ticker/validate/token/?$', validate_token, name='api_validate_token'),
    url(r'^match/ticker/invalidate/token/([0-9]+)/?$', invalidate_token, name='api_invalidate_token'),
    url(r'^update/score/field/([0-9]+)(/?|/json/?)$', update_score_field, name='update_score_field')
]