from django.contrib import admin

# Register your models here.
from ticker.models import Player


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'prename', 'lastname']
    list_editable = ['prename', 'lastname']

admin.register(Player, PlayerAdmin)