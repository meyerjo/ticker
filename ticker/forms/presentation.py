from django import forms

from ticker.models.presentation import Presentation, Slide


class PresentationForm(forms.ModelForm):

    class Meta:
        model = Presentation
        fields = ['team', 'name', 'description']


class SlideForm(forms.ModelForm):

    class Meta:
        model = Slide
        exclude = ['club', 'is_deleted']
