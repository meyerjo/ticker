from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

from ticker.models.matchstructure import Match
from ticker.models.player_clubs import Team


class League(models.Model):
    name = models.CharField(max_length=255)
    associated_season = models.ForeignKey('Season')
    teams = models.ManyToManyField(Team)
    league_key = models.CharField(max_length=255, default='')

    matches = models.ManyToManyField(Match)

    @staticmethod
    def get_other_leagues(league):
        if league.associated_season is None:
            return []
        season = league.associated_season
        return League.objects.filter(associated_season=season).filter(~Q(name=league.name))

    @staticmethod
    def league_matches_by_name(name):
        current_season = Season.get_current_season()
        league = League.objects.filter(name=name, associated_season=current_season).first()
        if league is None:
            return None, None, None
        # get the matches
        last_week = timezone.now() - timedelta(days=7)
        matches = league.matches.filter(match_time__date__gte=last_week, canceled=False, test_game=False)
        # filter the matches
        matches_today = []
        matches_not_today = []
        if matches is not None:
            matches_today = matches.filter(match_time__date=now().date()).order_by('match_time')
            matches_not_today = matches.filter(~Q(match_time__date=now().date())).order_by('match_time')
        return matches, matches_today, matches_not_today

    def add_team(self, team):
        leagues = League.objects.filter(teams__in=[team]).first()
        if leagues is not None:
            print('Team already in league {0}'.format(leagues.name))
            return False
        self.teams.add(team)
        return True

    def get_table(self):
        return self.teams.all()

    def get_name(self):
        return self.name

    def get_season(self):
        return self.associated_season

    def get_teams_in_league(self):
        return self.teams.all()

    def get_number_of_teams(self):
        return self.teams.all().count()

    def get_matches_in_league(self):
        return self.matches.filter(canceled=False).order_by('match_time')

    def get_all_possible_teams(self):
        teams_not_in_league = Team.objects.exclude(id__in=self.teams.values_list('id', flat=True))
        result = []
        for team in self.teams.all():
            result.append((team.id, team.get_name(), True))
        for team in teams_not_in_league:
            result.append((team.id, team.get_name(), False))
        return result

    @staticmethod
    def get_league_of_match(match):
        if match is None:
            return []
        if match.canceled:
            return None
        return League.objects.filter(matches=match).first()


class Season(models.Model):
    season_name = models.CharField(max_length=255)
    start_date = models.DateTimeField(default=timezone.now())
    end_date = models.DateTimeField(default=timezone.now())
    active = models.BooleanField(default=True)

    @staticmethod
    def get_seasons():
        return Season.objects.filter(active=True)

    @staticmethod
    def get_current_season():
        today = timezone.now()
        return Season.objects.filter(start_date__lte=today, end_date__gte=today, active=True).first()

    def season_is_on(self):
        now_date = timezone.now()
        return (now_date >= self.start_date) and (now_date <= self.end_date)

    def get_name(self):
        return self.season_name

    def get_leagues(self):
        return League.objects.filter(associated_season=self)

    def __str__(self):
        return 'Season from {0} to {1} ({2})'.format(
            self.start_date.strftime('%d.%m.%Y'),
            self.end_date.strftime('%d.%m.%Y'),
            'active' if self.active else 'in-active'
        )
