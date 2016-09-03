from django.db import models
from django.db import transaction
from django.db.models import ManyToManyField
from django.utils import timezone

from ticker.models.player_clubs import Player, Team


class Point(models.Model):
    canceled = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Point {0}'.format(
            '' if not self.canceled else '(canceled)'
        )


class Rules(models.Model):
    rule_name = models.CharField(max_length=32)

    def get_number_games(self):
        return 7

    def get_number_of_sets(self):
        return 5

    def validate(self, set_score_team_a, set_score_team_b):
        """
        Checks whether the score is valid
        :param set_score_team_a:
        :param set_score_team_b:
        :return:
        """
        if set_score_team_a < 0 or set_score_team_b < 0:
            return False
        if set_score_team_a > 15 or set_score_team_b > 15:
            return False
        if set_score_team_a == 15 and set_score_team_b == 15:
            return False
        if set_score_team_a > 11 and (set_score_team_a - set_score_team_b) > 2:
            return False
        if set_score_team_b > 11 and (set_score_team_b - set_score_team_a) > 2:
            return False
        return True

    def team_a_won(self, score):
        if score[0] == 11 and (score[0] - score[1]) >= 2:
            return True
        if score[0] > 11 and (score[0] - score[1]) == 2:
            return True
        if score[0] == 15 and score[1] == 14:
            return True
        return False

    def team_b_won(self, score):
        return self.team_a_won(list(reversed(score)))

    def set_started(self, score):
        return score != [0, 0]

    def __str__(self):
        return self.rule_name


class Set(models.Model):
    set_number = models.IntegerField(default=1)
    points_team_a = ManyToManyField(Point, related_name='points_team_a', blank=True)
    points_team_b = ManyToManyField(Point, related_name='points_team_b', blank=True)

    def add_point_team_a(self, rule):
        old_score = self.get_score()
        if rule.validate(old_score[0] + 1, old_score[1]):
            p = Point()
            p.save()
            self.points_team_a.add(p)
            return True
        return False

    def remove_point_team_a(self, rule):
        old_score = self.get_score()
        if rule.validate(old_score[0] - 1, old_score[1]):
            p = self.points_team_a.filter(canceled=False).order_by('-create_time').first()
            p.canceled=True
            p.save()
            return True
        return False

    def add_point_team_b(self, rule):
        old_score = self.get_score()
        if rule.validate(old_score[0], old_score[1]+1):
            p = Point()
            p.save()
            self.points_team_b.add(p)
            return True
        return False

    def remove_point_team_b(self, rule):
        old_score = self.get_score()
        if rule.validate(old_score[0], old_score[1]-1):
            p = self.points_team_b.filter(canceled=False).order_by('-create_time').first()
            p.canceled=True
            p.save()
            return True
        return False

    def is_started(self):
        return self.points_team_a.filter(canceled=False).count() != 0 or \
               self.points_team_b.filter(canceled=False).count() != 0

    def is_finished(self, rule):
        score = self.get_score()
        if not rule.validate(score[0], score[1]):
            return False
        if rule.team_a_won(score):
            return True
        if rule.team_b_won(score):
            return True
        return False

    def set_won_by_team_a(self, rule):
        score = self.get_score()
        return rule.team_a_won(score)

    def set_won_by_team_b(self, rule):
        score = self.get_score()
        return rule.team_b_won(score)

    def get_score(self):
        return [self.points_team_a.filter(canceled=False).count(),
                self.points_team_b.filter(canceled=False).count()]

    def __str__(self):
        return 'Set {0} ({1})'.format(self.set_number, ':'.join(map(str,self.get_score())))


class Game(models.Model):
    name = models.CharField(max_length=64)
    player_a = ManyToManyField(Player, related_name='player_a', blank=True)
    player_b = ManyToManyField(Player, related_name='player_b', blank=True)

    sets = ManyToManyField(Set, blank=True)
    game_types = (('single', 'Herreneinzel'),
                  ('womansingle', 'Dameneinzel'),
                  ('men_double', 'Herrendoppel'),
                  ('women_double', 'Frauendoppel'),
                  ('mixed', 'Mixed'))
    current_set = models.IntegerField(default=1)
    game_type = models.CharField(max_length=32, choices=game_types)

    def __str__(self):
        return '{0} {1} {2}'.format(self.name, self.game_type, '0')

    def in_progress(self):
        if self.current_set != 1:
            return True
        s = self.sets.filter(set_number=1).first()
        return s.is_started()

    def is_finished(self, rule):
        return self.is_won(rule)

    def get_set_score(self, rule):
        won_team_a = 0
        won_team_b = 0
        for set in self.sets.all():
            if set.set_won_by_team_a(rule):
                won_team_a += 1
            if set.set_won_by_team_b(rule):
                won_team_b += 1
        return [won_team_a, won_team_b]

    def is_won(self, rule):
        won_team_a, won_team_b = self.get_set_score(rule)
        if won_team_a == 3 or won_team_b == 3:
            return True
        return False

    def is_won_by(self, rule):
        won_team_a, won_team_b = self.get_set_score(rule)
        if won_team_a == 3 or won_team_b == 3:
            return 'team_a' if won_team_a == 3 else 'team_b'
        return None

    def get_sets(self):
        sets = self.sets.all()
        if len(sets) != 5:
            return 'Sets missing'
        all_sets = []
        for set in sets:
            tmp_score = set.get_score()
            tmp_score_str = ':'.join(map(str, tmp_score))
            all_sets.append(tmp_score_str)
        return ' '.join(all_sets)

    def get_set_objects(self):
        return self.sets.all()

    def get_current_set(self):
        current_set = self.current_set
        set = self.sets.filter(set_number=current_set).first()
        return set

    def get_points(self):
        sets = self.sets.all()
        points_team_a = 0
        points_team_b = 0
        for set in sets:
            points_team_a += set.get_score()[0]
            points_team_b += set.get_score()[1]
        return [points_team_a, points_team_b]

    def get_match(self):
        return Match.objects.filter(games__id=self.id).first()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Game, self).save(force_insert, force_update, using, update_fields)
        if self.sets.count() == 0:
            with transaction.atomic():
                for i in range(0, 5):
                    set = Set(set_number=i+1)
                    set.save()
                    self.sets.add(set)


class Match(models.Model):
    match_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now=True)
    canceled = models.BooleanField(default=False)
    rule = models.ForeignKey(Rules)
    team_a = models.ForeignKey(Team, related_name='team_a')
    team_b = models.ForeignKey(Team, related_name='team_b')
    games = ManyToManyField(Game, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Match, self).save(force_insert, force_update, using, update_fields)
        if self.games.count() == 0:
            games_dict = [
                dict(games_name='1. Herreneinzel', games_type='single'),
                dict(games_name='2. Herreneinzel', games_type='single'),
                dict(games_name='Dameneinzel', games_type='womansingle'),
                dict(games_name='1. Herrendoppel', games_type='men_double'),
                dict(games_name='2. Herrendoppel', games_type='men_double'),
                dict(games_name='Gemischtes Doppel', games_type='mixed'),
                dict(games_name='Damendoppel', games_type='women_double'),
            ]
            with transaction.atomic():
                for tmp_dict in games_dict:
                    g = Game(game_type=tmp_dict['games_type'],
                             name=tmp_dict['games_name'])
                    g.save()
                    self.games.add(g)


    @staticmethod
    def all_matches():
        matches = Match.objects.filter(canceled=False)
        return matches


    @staticmethod
    def get_matches():
        import datetime
        current_day = datetime.datetime.now()
        matches = Match.objects.filter(canceled=False,
                                       match_time__day=current_day)
        return matches

    def get_all_games(self):
        return self.games.all()

    def get_team_names(self):
        return [self.team_a.get_name(), self.team_b.get_name()]

    def get_score(self):
        games = self.get_all_games()
        score_team_a = 0
        score_team_b = 0
        for game in games:
            if not game.is_finished(self.rule):
                continue
            res = game.is_won_by(self.rule)
            if res is None:
                continue
            if res == 'team_a':
                score_team_a +=1
            elif res == 'team_b':
                score_team_b +=1
        return [score_team_a, score_team_b]

    def get_fields(self):
        if self.team_a is None:
            return []
        return self.team_a.get_fields()

    def get_point_score(self):
        games = self.get_all_games()
        score = [0, 0]
        for game in games:
            score[0] += game.get_points()[0]
            score[1] += game.get_points()[1]
            print(game.get_points(), score)
        return score

    def get_set_score(self):
        games = self.get_all_games()
        score = [0, 0]
        for game in games:
            score[0] += game.get_set_score(self.rule)[0]
            score[1] += game.get_set_score(self.rule)[1]
        return score

    def has_lineup(self):
        for game in self.games.all():
            if game.player_a.count() == 0:
                return False
        return True

    def __str__(self):
        return 'Match {0}: {1}:{2} Result: {3}:{4}'.format(
            self.match_time.strftime('%d.%m.%Y %H:%M'),
            self.team_a.get_name(),
            self.team_b.get_name(),
            self.get_score()[0],
            self.get_score()[1]
        )