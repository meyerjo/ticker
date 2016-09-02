from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import CASCADE

from ticker.models import Match, Game


class PlayingField(models.Model):
    field_name = models.CharField(max_length=255)

    def get_name(self):
        return self.field_name

    def get_game(self):
        field_allocations = FieldAllocation.objects.filter(field=self, is_active=True, end_allocation=None)
        if field_allocations.exists():
            if field_allocations.count() != 1:
                field_allocations = field_allocations.order_by('-create_time')
            return field_allocations[0].game
        return None

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
