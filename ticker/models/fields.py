from django.db import models
from django.db.models import CASCADE

from ticker.models import Match, Game


class Field(models.Model):
    field_name = models.CharField(max_length=255)
    

class FieldAllocation(models.Model):
    field = models.ForeignKey(Field, CASCADE)
    game = models.ForeignKey(Game, CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    end_allocation = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
