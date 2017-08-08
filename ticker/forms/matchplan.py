from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, BaseModelFormSet, Select, ModelMultipleChoiceField, HiddenInput, RadioSelect, \
    SelectMultiple

from ticker.models import Match, Game, Team, Player


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['match_time', 'rule', 'team_a', 'team_b']


class GameLineUpFormSet(BaseModelFormSet):


    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        player_game_counter = dict()
        # check for double players
        for form in self.forms:
            tmp_fields = ['player_a', 'player_b', 'player_a_double', 'player_b_double']
            for f in tmp_fields:
                if f not in form.cleaned_data:
                    continue
                if form.cleaned_data[f].first() is not None:
                    name = form.cleaned_data[f].first().get_name()
                    if name in player_game_counter:
                        player_game_counter[name] += 1
                    else:
                        player_game_counter[name] = 1
            players_violating = []
            for player, value in player_game_counter.items():
                if value > 2:
                    players_violating.append(player)
            if len(players_violating) > 0:
                raise ValidationError('Player has too many games: {0}'.format(
                    ','.join(players_violating)
                ))

        player_twice_in_same_game_type = []
        gametype_player_counter = dict()
        for form in self.forms:
            if 'id' not in form.cleaned_data:
                continue
            game = form.cleaned_data['id']
            # game = Game.objects.filter(id=id).first()
            if game.game_type not in gametype_player_counter:
                gametype_player_counter[game.game_type] = dict()
            tmp_fields = ['player_a', 'player_b', 'player_a_double', 'player_b_double']
            for f in tmp_fields:
                if f not in form.cleaned_data:
                    continue
                if form.cleaned_data[f].first() is not None:
                    name = form.cleaned_data[f].first().get_name()
                    if name in gametype_player_counter[game.game_type]:
                        gametype_player_counter[game.game_type][name] += 1
                        player_twice_in_same_game_type.append(name)
                    else:
                        gametype_player_counter[game.game_type][name] = 1

        if len(player_twice_in_same_game_type) > 0:
            raise ValidationError('Player too many games in the same category: {0}'.format(
                ','.join(player_twice_in_same_game_type)
            ))

class M2M_Select(SelectMultiple):
    allow_multiple_selected = False




class GameLineUpForm(forms.ModelForm):

    player_a_double = ModelMultipleChoiceField( required=False,   queryset=Player.objects.all())
    player_b_double = ModelMultipleChoiceField( required=False,  queryset=Player.objects.all())

    def save(self, commit=False):
        print(self.__dict__)
        super(GameLineUpForm, self).save(commit)
        self.player_a.clear()
        players_a = self.cleaned_data['player_a'] | self.cleaned_data['player_a_double']
        print(players_a)
        self.player_a.add(players_a)
        print(self.player_a.all())
        self.player_b.clear()
        self.player_b.add(self.cleaned_data['player_b'] | self.cleaned_data['player_b_double'])
        #self.cleaned_data['player_b'] = self.cleaned_data['player_b'] | self.cleaned_data['player_b_double']

    def get_game(self):
        return Game.objects.filter(id=self.instance.id).first()

    def __init__(self, *args, **kwargs):
        super(GameLineUpForm, self).__init__(*args, **kwargs)

        game = Game.objects.filter(id=self.instance.id).first()
        teams = Team.objects.filter(team_a__games__in=[game]) | Team.objects.filter(team_b__games__in=[game])
        if game:
            self.fields['player_a'].required = False
            self.fields['player_b'].required = False
            self.fields['player_a_double'].required = False
            self.fields['player_b_double'].required = False
            if game.game_type == 'men_double' or game.game_type == 'single':
                self.fields['player_a'].queryset = teams[0].players.filter(sex='male')
                self.fields['player_b'].queryset = teams[1].players.filter(sex='male')
                if game.game_type == 'men_double':
                    self.fields['player_a_double'].queryset = teams[0].players.filter(sex='male')
                    self.fields['player_b_double'].queryset = teams[1].players.filter(sex='male')
                    self.fields['player_a_double'].required = False
                    self.fields['player_b_double'].required = False

                    players = game.player_a.all()


                    # self.fields['player_a_double'].initial = game.player_b.all()[1].id

                else:
                    self.fields['player_a_double'].widget = HiddenInput()
                    self.fields['player_b_double'].widget = HiddenInput()
            elif game.game_type == 'womansingle' or game.game_type == 'women_double':
                self.fields['player_a'].queryset = teams[0].players.filter(sex='female')
                self.fields['player_b'].queryset = teams[1].players.filter(sex='female')
                if game.game_type == 'women_double':
                    self.fields['player_a_double'].queryset = teams[0].players.filter(sex='female')
                    self.fields['player_b_double'].queryset = teams[1].players.filter(sex='female')
                    self.fields['player_a_double'].required = False
                    self.fields['player_b_double'].required = False
                else:
                    self.fields['player_a_double'].widget = HiddenInput()
                    self.fields['player_b_double'].widget = HiddenInput()
            else:
                self.fields['player_a'].queryset = teams[0].players.filter(sex='male')
                self.fields['player_a_double'].queryset = teams[0].players.filter(sex='female')
                self.fields['player_b'].queryset = teams[1].players.filter(sex='male')
                self.fields['player_b_double'].queryset = teams[1].players.filter(sex='female')
                self.fields['player_a_double'].required = False
                self.fields['player_b_double'].required = False

    def is_valid(self):
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            return True
        if 'player_a' not in self.cleaned_data:
            return False
        if 'player_b' not in self.cleaned_data:
            return False

        player_a = self.cleaned_data['player_a']
        player_b = self.cleaned_data['player_b']
        player_a_double = self.cleaned_data['player_a_double']
        player_b_double = self.cleaned_data['player_b_double']

        if player_a.count() == 0:
            return False
        if player_b.count() == 0:
            return False

        if 'double' in game.game_type or game.game_type == 'mixed':
            if player_a_double.count() == 0:
                return False
            if player_b_double.count() == 0:
                return False
            if player_a[0] == player_a_double[0]:
                return False
            if player_b[0] == player_b_double[0]:
                return False
        return super(GameLineUpForm, self).is_valid()

    def clean(self):
        cleaned_data = super(GameLineUpForm, self).clean()
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            return True

        player_a = cleaned_data.get('player_a', [])
        player_b = cleaned_data.get('player_b', [])
        player_a_double = cleaned_data.get('player_a_double', [])
        player_b_double = cleaned_data.get('player_b_double', [])

        if len(player_a) == 0:
            raise forms.ValidationError(
                'No player selected'
            )
        if len(player_b) == 0:
            raise forms.ValidationError(
                'No player selected'
            )

        if 'double' in game.game_type or game.game_type == 'mixed':
            if len(player_a_double) == 0:
                raise forms.ValidationError(
                    'Double player not selected'
                )
            if len(player_b_double) == 0:
                raise forms.ValidationError(
                    'Double player not selected'
                )
            if player_a[0] == player_a_double[0]:
                raise forms.ValidationError(
                    'One player cannot play both roles in one game'
                )
            if player_b[0] == player_b_double[0]:
                raise forms.ValidationError(
                    'One player cannot play both roles in one game'
                )

    class Meta:
        model = Game
        fields = ['id', 'name', 'player_a', 'player_b']
        widgets = {
            'player_a': M2M_Select,
            'player_b': M2M_Select,
            'id': HiddenInput(),
            'name': HiddenInput()
        }

