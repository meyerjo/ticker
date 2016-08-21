from django.db import models

from ticker.models.matchstructure import Match
from ticker.models.player_clubs import Team


class League(models.Model):
    name = models.CharField(max_length=255)

    teams = models.ForeignKey(Team)

    matches = models.ForeignKey(Match)

    def add_team(self):
        pass

    def get_table(self):
        pass