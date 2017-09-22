from django.contrib import admin

# Register your models here.
from ticker.models import Club, ColorDefinition, DefinableColor, League
from ticker.models import FieldAllocation
from ticker.models import Game
from ticker.models import Match
from ticker.models import Player
from ticker.models import PlayingField
from ticker.models import Profile
from ticker.models import Rules
from ticker.models import Set
from ticker.models import Team
from ticker.models.presentation import Presentation, PresentationSlideTeam, Slide


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'prename', 'lastname', 'sex', 'birth_date']
    list_editable = ['prename', 'lastname', 'sex', 'birth_date']


admin.site.register(Player, PlayerAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'team_name']
    list_editable = ['team_name']


admin.site.register(Team, TeamAdmin)


class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'match_time', 'team_a', 'team_b', 'get_score']


admin.site.register(Match, MatchAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'game_type', 'get_sets']


admin.site.register(Game, GameAdmin)


class SetAdmin(admin.ModelAdmin):
    list_display = ['id', 'set_number', 'get_score']


admin.site.register(Set, SetAdmin)


class RuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'rule_name']


admin.site.register(Rules, RuleAdmin)


class ClubAdmin(admin.ModelAdmin):
    list_display = ['id', 'club_name']


admin.site.register(Club, ClubAdmin)


class PlayingFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'field_name']


admin.site.register(PlayingField, PlayingFieldAdmin)


class FieldAllocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'field']


admin.site.register(FieldAllocation, FieldAllocationAdmin)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'associated_club']


admin.site.register(Profile, ProfileAdmin)


class DefinableColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(DefinableColor, DefinableColorAdmin)


class ColorDefinitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'club', 'color_definition', 'color_hexcode']


admin.site.register(ColorDefinition, ColorDefinitionAdmin)


class LeagueAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'associated_season', 'get_number_of_teams']
    list_display_links = ['id', 'name']

admin.site.register(League, LeagueAdmin)


class PresentationAdmin(admin.ModelAdmin):
    list_display = ['id', 'team', 'name', 'displayed']

admin.site.register(Presentation, PresentationAdmin)


class PresentationSlideTeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'slide', 'slide_number', 'slide_visible', 'create_time']

admin.site.register(PresentationSlideTeam, PresentationSlideTeamAdmin)


class SlideAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'content_type', 'content_path', ]

admin.site.register(Slide, SlideAdmin)


class TeamPlayerAssociationAdmin(admin.ModelAdmin):
    list_display = ['id', 'team', 'player', 'start_association', 'end_association']

admin.site.register(TeamPlayerAssociation, TeamPlayerAssociationAdmin)
