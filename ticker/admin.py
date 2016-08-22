from django.contrib import admin

# Register your models here.
from ticker.models import Player
from ticker.models import Team


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'prename', 'lastname', 'sex', 'birth_date']
    list_editable = ['prename', 'lastname', 'sex', 'birth_date']

admin.site.register(Player, PlayerAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'team_name']
    list_editable = ['team_name']

admin.site.register(Team, TeamAdmin)
