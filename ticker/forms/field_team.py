from django.forms import ModelForm, ChoiceField, CharField, Form, MultipleChoiceField
from django.utils.safestring import mark_safe

from ticker.models import PlayingField, Team


class FieldTeamForm(Form):
    field_name = CharField(max_length=255)
    teams = MultipleChoiceField(choices=[])

    def __init__(self, club, *args, **kwargs):
        super(FieldTeamForm, self).__init__(*args, **kwargs)
        self.fields['teams'] = MultipleChoiceField(
            choices=[
                (int(t.id), t.team_name) for t in Team.objects.filter(parent_club=club)
            ]
        )

    def as_tr(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return mark_safe('<tr><td></td>' + self._html_output(
            normal_row='<td>%(errors)s%(field)s%(help_text)s</td>',
            error_row='<tr><td colspan="2">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False) + '<td></td></tr>')
