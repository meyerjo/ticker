from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE


class Club(models.Model):
    club_name = models.CharField(max_length=255)

    def add_team(self, teamname):
        pass

    def get_name(self):
        return self.club_name



class Player(models.Model):
    prename = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)

    birth_date = models.DateTimeField(null=True, blank=True)

    def get_name(self):
        return '{0} {1}'.format(self.prename, self.lastname)


class Team(models.Model):
    team_name = models.CharField(max_length=255)
    players = models.ManyToManyField(Player)

    def add_player(self, player):
        assert (isinstance(player, Player))
        self.players.add(player)

    def remove_player(self, player):
        self.players.remove(player)

    def get_name(self):
        return self.team_name


class TeamPlayerAssociation(models.Model):
    team = models.ForeignKey(Team, CASCADE)
    player = models.ForeignKey(Player, CASCADE)

    start_association = models.DateField()
    end_association = models.DateField()


class Profile(models.Model):
    user = models.OneToOneField(User, CASCADE)

    associated_club = models.ForeignKey(Club, CASCADE)

    def __str__(self):
        return '{0} {1}'.format(self.user.get_full_name(), str(self.associated_club))