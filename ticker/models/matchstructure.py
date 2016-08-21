from django.db import models
from django.db.models import ManyToManyField

from ticker.models.player_clubs import Player


class Point(models.Model):
    canceled = models.BooleanField(default=False)

class Set(models.Model):
    set_number = models.IntegerField(default=1)
    points_team_a = ManyToManyField(Point)
    points_team_b = ManyToManyField(Point)

class Game(models.Model):
    name = models.CharField(max_length=64)
    player_a = ManyToManyField(Player)
    player_b = ManyToManyField(Player)

    sets = ManyToManyField(Set)
    game_types = (('single', 'Einzel'),
                  ('men_double', 'Herrendoppel'),
                  ('women_double', 'Frauendoppel'),
                  ('mixed', 'Mixed'))

class Match(models.Model):
    match_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now=True)
    games = ManyToManyField(Game)


