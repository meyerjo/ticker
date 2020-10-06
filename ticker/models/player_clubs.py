from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.utils.timezone import now


class Club(models.Model):
    club_name = models.CharField(max_length=255)
    fields = models.ManyToManyField('PlayingField', blank=True)

    def add_team(self, teamname):
        pass

    def get_name(self):
        return self.club_name

    def get_associated_profile(self):
        return Profile.objects.filter(associated_club=self)

    def get_teams(self):
        return Team.objects.filter(parent_club=self).order_by('team_name')

    def get_next_team_index(self):
        return Team.objects.filter(parent_club=self).count() + 1

    def get_players(self):
        return Player.objects.filter(teamplayerassociation__team__parent_club=self)

    def get_ten_players(self):
        return Player.objects.filter(teamplayerassociation__team__parent_club=self)[:9]

    def get_fields(self):
        from ticker.models import PlayingField
        field_ids = PlayingField.objects.filter(team__parent_club=self).values_list('id', flat=True).distinct()
        fields = PlayingField.objects.filter(id__in=field_ids)
        return fields

    def __str__(self):
        return self.get_name()


class Player(models.Model):
    prename = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)

    possible_sex = (('female', 'Weiblich'),
                    ('male', 'Maennlich'))
    sex = models.CharField(max_length=32, choices=possible_sex)
    birth_date = models.DateTimeField(null=True, blank=True)

    def get_name(self):
        return '{0} {1}'.format(self.prename, self.lastname)

    @staticmethod
    def get_by_ids(ids):
        return Player.objects.filter(id__in=ids).order_by('sex', 'lastname', 'prename')


    def __str__(self):
        return '{0} {1}'.format(self.prename, self.lastname)


class Team(models.Model):
    parent_club = models.ForeignKey(Club, CASCADE, default=1)
    team_name = models.CharField(max_length=255)
    players = models.ManyToManyField(Player, blank=True)
    fields = models.ManyToManyField('PlayingField', blank=True)

    def add_player(self, player):
        assert (isinstance(player, Player))
        self.players.add(player)

    def remove_player(self, player):
        self.players.remove(player)

    def get_name(self):
        return self.team_name

    def get_players(self):
        """
        Retrieves all players for the team from the teamplayerassociations
        :return:
        """
        # retrieve the associations
        team_player_associations = TeamPlayerAssociation.get_by_team(self)
        # retrieve the player ids
        player_ids = team_player_associations.values_list('player__id', flat=True)
        return Player.get_by_ids(player_ids)

    def get_other_teams(self):
        teams = Team.objects.filter(parent_club=self.parent_club).exclude(id=self.id)
        print(teams)
        return teams

    def get_fields_annotated(self):
        parent_club_fields = self.parent_club.fields.filter(id__in=self.fields.all().values_list('id', flat=True))
        other_club_fields = self.parent_club.fields.exclude(id__in=self.fields.all().values_list('id', flat=True))
        result = []
        for field in parent_club_fields:
            result.append((field.id, field.get_name(), 1))
        for field in other_club_fields:
            result.append((field.id, field.get_name(), 0))
        return result

    def get_fields(self):
        return self.fields.all()

    def __str__(self):
        return self.team_name


class TeamPlayerAssociation(models.Model):
    team = models.ForeignKey(Team, CASCADE)
    player = models.ForeignKey(Player, CASCADE)

    start_association = models.DateField()
    end_association = models.DateField()

    @staticmethod
    def get_by_team(team, date=None):
        """
        Returns the teamplayerassociation for the given team at the given date. If date=None for the given date
        :param date:
        :return:
        """
        if date is None:
            date = now()
        return TeamPlayerAssociation.objects.filter(
            team=team, start_association__gte=date.date(), end_association__lt=date.date())


class Profile(models.Model):
    user = models.OneToOneField(User, CASCADE)

    associated_club = models.ForeignKey(Club, CASCADE)

    def __str__(self):
        return '{0} {1}'.format(self.user.get_full_name(), str(self.associated_club))


class DefinableColor(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return 'Color-Definition: {0}'.format(self.name)


class ColorDefinition(models.Model):
    club = models.ForeignKey(Club, CASCADE)
    color_definition = models.ForeignKey(DefinableColor, on_delete=models.CASCADE)
    color_hexcode = models.CharField(max_length=32)

    def __str__(self):
        return '{0} has {1} filled with {2}'.format(
            self.club.get_name(),
            self.color_definition.name,
            self.color_hexcode
        )

    class Meta:
        unique_together = ('club', 'color_definition')
