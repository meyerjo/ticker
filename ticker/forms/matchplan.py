from django import forms

from ticker.models import Match


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['match_time', 'rule', 'team_a', 'team_b']