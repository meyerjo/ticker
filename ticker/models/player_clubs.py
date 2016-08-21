from django.db import models


class Club(models.Model):
    club_name = models.CharField(max_length=255)

    def add_team(self, teamname):
        pass

class Team(models.Model):
    team_name = models.CharField(max_length=255)
    players = models.ManyToManyField(Player)

    def add_player(self, player):
        pass

    def remove_player(self, player):
        pass

class Player(models.Model):
    prename = models.CharField()
    lastname = models.CharField()

    birth_date = models.DateTimeField(null=True, blank=True)

    def get_name(self):
        pass