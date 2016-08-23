from django import views
from django.conf.urls import url

from ticker.views.api import *

urlpatterns = [
    url(r'^club/add/?$', add_club, name='club_add'),
    url(r'^club/([0-9]+)/addteam/?$', add_team, name='team_add'),
    url(r'^club/edit/?$', edit_club, name='club_edit'),

    url(r'^field/add?$', not_yet_implemented, name='field_add'),
    url(r'^field/([0-9]+)/add/club/([0-9]+)/??$', not_yet_implemented, name='field_add_to_club'),

]