import logging

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, BaseModelFormSet, Select, ModelMultipleChoiceField, HiddenInput, RadioSelect, \
    SelectMultiple, ModelChoiceField

from ticker.models import Match, Game, Team, Player, TeamPlayerAssociation


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
                if form.cleaned_data[f] is not None:
                    name = form.cleaned_data[f].get_name()
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
                if form.cleaned_data[f] is not None:
                    name = form.cleaned_data[f].get_name()
                    if name in gametype_player_counter[game.game_type]:
                        gametype_player_counter[game.game_type][name] += 1
                        player_twice_in_same_game_type.append(name)
                    else:
                        gametype_player_counter[game.game_type][name] = 1

        if len(player_twice_in_same_game_type) > 0:
            raise ValidationError('Player too many games in the same category: {0}'.format(
                ','.join(player_twice_in_same_game_type)
            ))


class GameLineUpForm(forms.ModelForm):
    player_a = ModelChoiceField(required=False, queryset=Player.objects.all())
    player_b = ModelChoiceField(required=False, queryset=Player.objects.all())
    player_a_double = ModelChoiceField( required=False,   queryset=Player.objects.all())
    player_b_double = ModelChoiceField( required=False,  queryset=Player.objects.all())

    def save(self, commit=False):
        # get the game
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            raise ValidationError('Game is none')

        if not hasattr(self, 'cleaned_data'):
            raise ValidationError('Cleaned data field is missing')

        # clear the data
        # save the player lineup
        game.player_a.clear()
        players_a = [self.cleaned_data['player_a']]
        if 'player_a_double' in self.cleaned_data:
            if self.cleaned_data['player_a_double'] is not None:
                players_a.append(self.cleaned_data['player_a_double'])
        game.player_a.add(*players_a)
        #
        game.player_b.clear()
        players_b = [self.cleaned_data['player_b']]
        if 'player_b_double' in self.cleaned_data:
            if self.cleaned_data['player_b_double'] is not None:
                players_b.append(self.cleaned_data['player_b_double'])
        game.player_b.add(*players_b)
        game.save()

    def get_game(self):
        return Game.objects.filter(id=self.instance.id).first()

    def __init__(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        super(GameLineUpForm, self).__init__(*args, **kwargs)
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            return

        data = dict()
        players_a = game.player_a.all()
        players_b = game.player_b.all()
        logger.debug('Game ID: {0} Players Team A: {1}'.format(game.id, str(players_a)))
        logger.debug('Game ID: {0} Players Team B: {1}'.format(game.id, str(players_b)))

        if len(players_a) >= 1:
            data['player_a'] = players_a[0].id
            if len(players_a) == 2:
                data['player_a_double'] = players_a[1].id

        if len(players_b) >= 1:
            data['player_b'] = players_b[0].id
            if len(players_b) == 2:
                data['player_b_double'] = players_b[1].id

        # for the mixed doubles we switch the values if the first player is female
        # (This is not for discrimination but an early design decision ;-))
        if game.game_type == 'mixed':
            for team in ['player_a', 'player_b']:
                p1 = Player.objects.filter(id=data[team]).first()
                if p1 is None:
                    continue
                if p1.sex == 'female':
                    data[team], data[team + '_double'] = data[team + '_double'], data[team]

        logger.debug('Game ID: {0} Players: {1}'.format(game.id, str(data)))

        super(GameLineUpForm, self).__init__(initial=data, *args, **kwargs)

        # get the teams
        teams = Team.objects.filter(team_a__games__in=[game]) | \
                Team.objects.filter(team_b__games__in=[game])
        if game:
            import datetime
            now_date = datetime.date.today()
            start_date = datetime.date(year=now_date.year, month=8, day=1)
            end_date = datetime.date(year=now_date.year + 1, month=7, day=31)

            team_players_team_a = TeamPlayerAssociation.objects.filter(team=teams[0], start_association=start_date, end_association=end_date)
            team_players_team_b = TeamPlayerAssociation.objects.filter(team=teams[1], start_association=start_date, end_association=end_date)

            sex_male_team_a = teams[0].players.filter(sex='male')
            sex_female_team_a = teams[0].players.filter(sex='female')
            sex_male_team_b = teams[1].players.filter(sex='male')
            sex_female_team_b = teams[1].players.filter(sex='female')

            self.fields['player_b'].required = False
            self.fields['player_a_double'].required = False
            self.fields['player_b_double'].required = False
            # if it is not a double or mixed we can ignore this result
            if 'double' not in game.game_type and game.game_type != 'mixed':
                self.fields['player_a_double'].widget = HiddenInput()
                self.fields['player_b_double'].widget = HiddenInput()

            if game.game_type in ['men_double', 'single']:
                # self.fields['player_a'].queryset = teams[0].players.filter(sex='male')
                self.fields['player_a'].queryset = sex_male_team_a
                self.fields['player_b'].queryset = sex_male_team_b
                if game.game_type == 'men_double':
                    self.fields['player_a_double'].queryset = sex_male_team_a
                    self.fields['player_b_double'].queryset = sex_male_team_b
            elif game.game_type in ['women_double', 'womansingle']:
                self.fields['player_a'].queryset = sex_female_team_a
                self.fields['player_b'].queryset = sex_female_team_b
                if game.game_type == 'women_double':
                    self.fields['player_a_double'].queryset = sex_female_team_a
                    self.fields['player_b_double'].queryset = sex_female_team_b
            else:
                self.fields['player_a'].queryset = sex_male_team_a
                self.fields['player_a_double'].queryset = sex_female_team_a
                self.fields['player_b'].queryset = sex_male_team_b
                self.fields['player_b_double'].queryset = sex_female_team_b

    def is_valid(self):
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            return True
        # first player has to be set in any case
        if 'player_a' not in self.cleaned_data:
            return False
        if 'player_b' not in self.cleaned_data:
            return False

        player_a = self.cleaned_data.get('player_a', None)
        player_b = self.cleaned_data.get('player_b', None)
        player_a_double = self.cleaned_data.get('player_a_double', None)
        player_b_double = self.cleaned_data.get('player_b_double', None)

        # first player has to be set
        if player_a is None:
            return False
        if player_b is None:
            return False

        if 'double' in game.game_type or game.game_type == 'mixed':
            # if it is a double ..

            # .. second player has to be set
            if player_a_double is None:
                return False
            if player_b_double is None:
                return False

            # .. players should not be the same
            if player_a == player_a_double:
                return False
            if player_b == player_b_double:
                return False
        return super(GameLineUpForm, self).is_valid()

    def clean(self):
        cleaned_data = super(GameLineUpForm, self).clean()
        game = Game.objects.filter(id=self.instance.id).first()
        if game is None:
            return True

        player_a = cleaned_data.get('player_a', None)
        player_b = cleaned_data.get('player_b', None)
        player_a_double = cleaned_data.get('player_a_double', None)
        player_b_double = cleaned_data.get('player_b_double', None)

        if player_a is None:
            raise forms.ValidationError(
                'No player selected'
            )
        if player_b is None:
            raise forms.ValidationError(
                'No player selected'
            )

        if 'double' in game.game_type or game.game_type == 'mixed':
            if player_a_double is None:
                raise forms.ValidationError(
                    'Double player not selected'
                )
            if player_b_double is None:
                raise forms.ValidationError(
                    'Double player not selected'
                )
            if player_a.id == player_a_double.id:
                raise forms.ValidationError(
                    'One player cannot play both roles in one game'
                )
            if player_b.id == player_b_double.id:
                raise forms.ValidationError(
                    'One player cannot play both roles in one game'
                )

    class Meta:
        model = Game
        fields = ['id', 'name', 'player_a', 'player_b']
        widgets = {
            'id': HiddenInput(),
            'name': HiddenInput()
        }

