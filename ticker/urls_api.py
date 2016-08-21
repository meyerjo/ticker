from django import views
from django.conf.urls import url

from ticker.views.api import *

urlpatterns = [
    url(r'^club/add/?', add_club),
    url(r'^club/\{club\}/addteam/\{team\}$', add_team),
]