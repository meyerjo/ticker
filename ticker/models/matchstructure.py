from django.db import models
from django.db.models import ManyToManyField

from ticker.models.player_clubs import Player, Team


class Point(models.Model):
    canceled = models.BooleanField(default=False)

class Rules(models.Model):
    rule_name = models.CharField(max_length=32)

    def get_number_games(self):
        return 7

    def validate(self, set_score_team_a, set_score_team_b):
        if set_score_team_a < 0 or set_score_team_b < 0:
            return False
        if set_score_team_a > 15 or set_score_team_b > 15:
            return False
        if set_score_team_a <= 10 and set_score_team_b <= 10:
            return False
        if (set_score_team_a == 15) and (set_score_team_b == 14) or \
            (set_score_team_a == 14) and (set_score_team_b == 15):
            return True
        diff = abs(set_score_team_b - set_score_team_a)
        if set_score_team_a >= 11 and diff == 2:
            return True
        if set_score_team_b >= 11 and diff == 2:
            return True
        return False


class Set(models.Model):
    set_number = models.IntegerField(default=1)
    points_team_a = ManyToManyField(Point, related_name='points_team_a')
    points_team_b = ManyToManyField(Point, related_name='points_team_b')

    def add_point_team_a(self):
        pass

    def remove_point_team_a(self):
        pass

    def add_point_team_b(self):
        pass

    def remove_point_team_b(self):
        pass

    def is_started(self):
        return self.points_team_a.filter(canceled=False).count() != 0 or \
               self.points_team_b.filter(canceled=False).count() != 0

    def is_finished(self):

        return False

    def get_score(self):
        return [self.points_team_a.filter(canceled=False).count(),
                self.points_team_b.filter(canceled==False).count()]


class Game(models.Model):
    name = models.CharField(max_length=64)
    player_a = ManyToManyField(Player, related_name='player_a')
    player_b = ManyToManyField(Player, related_name='player_b')

    sets = ManyToManyField(Set)
    game_types = (('single', 'Einzel'),
                  ('men_double', 'Herrendoppel'),
                  ('women_double', 'Frauendoppel'),
                  ('mixed', 'Mixed'))
    game_type = models.CharField(max_length=32, choices=game_types)

    def __str__(self):
        return '{0} {1} {2}'.format(self.name, self.game_type, '0')

    def is_finished(self):
        return False

    def is_won(self):
        # TODO: change that
        return False

    def get_sets(self):
        sets = self.sets.all()
        if len(sets) != 5:
            return 'error'
        sets = []
        for set in sets:
            sets.append(':'.join(set.get_score()))
        return ' '.join(sets)


class Match(models.Model):
    match_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now=True)
    canceled = models.BooleanField(default=False)
    rule = models.ForeignKey(Rules)
    team_a = models.ForeignKey(Team, related_name='team_a')
    team_b = models.ForeignKey(Team, related_name='team_b')
    games = ManyToManyField(Game)

    @staticmethod
    def all_matches():
        matches = Match.objects.filter(canceled=True)
        return matches

    def get_all_games(self):
        return self.objects.games()

    def get_team_names(self):
        return [self.team_a.get_name(), self.team_b.get_name()]

    def get_score(self):
        games = self.get_all_games()
        score_team_a = 0
        score_team_b = 0
        for game in games:
            if not game.is_finished():
                continue
            if game.is_won():
                score_team_a +=1
            else:
                score_team_b +=1
        return [score_team_a, score_team_b]


