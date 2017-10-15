from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE

from ticker.models import Game, Team


class PlayingField(models.Model):
    field_name = models.CharField(max_length=255)

    def __str__(self):
        return 'ID: {0} Name: {1}'.format(self.id, self.field_name)

    def get_name(self):
        return self.field_name

    def get_game(self):
        field_allocations = FieldAllocation.objects.filter(field=self, is_active=True, end_allocation=None)
        if field_allocations.exists():
            if field_allocations.count() != 1:
                field_allocations = field_allocations.order_by('-create_time')
            return field_allocations[0].game
        return None

    def get_teams(self):
        return Team.objects.filter(fields__in=[self])

    def has_token(self):
        tokens = PresentationToken.objects.filter(field=self, is_used=False,)
        return tokens.count() != 0

    def get_token(self):
        tokens = PresentationToken.objects.filter(field=self, is_used=False,)
        return tokens.first()


class FieldAllocation(models.Model):
    field = models.ForeignKey(PlayingField, CASCADE)
    game = models.ForeignKey(Game, CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    end_allocation = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '{0} assigned to {1} {2}'.format(
            self.game.name,
            self.field.field_name,
            ' is active' if self.is_active else ' is outdated'
        )


class PresentationToken(models.Model):
    user = models.ForeignKey(User)
    field = models.ForeignKey(PlayingField)
    token = models.CharField(max_length=32)

    is_used = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)

    usage_time = models.DateTimeField(null=True, blank=True)

    last_action = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '<Token: {0} for field {1} ({2})>'.format(
            self.token,
            self.field,
            'used' if self.is_used else 'unused'
        )

    @staticmethod
    def is_valid(token):
        t = PresentationToken.objects.filter(token=token, is_used=False)
        return True if t.first() is not None else False
