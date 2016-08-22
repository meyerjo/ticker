from django.db import models

from ticker.models.matchstructure import Match
from ticker.models.player_clubs import Team


class League(models.Model):
    name = models.CharField(max_length=255)

    teams = models.ManyToManyField(Team)

    matches = models.ManyToManyField(Match)

    def generate_matches(self):
        teams = self.teams.all()
        for team in teams:
            for team_b in teams:
                if team.id == team_b.id:
                    continue

        pass

    def add_team(self, team):
        leagues = League.objects.filter(teams__in=[team]).first()
        if leagues is not None:
            print('Team already in league {0}'.format(leagues.name))
            return False
        self.teams.add(team)
        return True

    def get_table(self):
        pass

class Season(models.Model):
    season_name = models.CharField(max_length=255)

    leagues = models.ManyToManyField(League)