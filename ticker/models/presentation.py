from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db import models

from ticker.models import Club
from ticker.models import PlayingField
from ticker.models import Team



class Slide(models.Model):

    club = models.ForeignKey(Club)

    title = models.CharField(max_length=255)
    POSSIBLE_CONTENT_TYPE = [('score', 'Score'),
                             ('advertisement_photo', 'Werbung (Foto)'),
                             ('advertisement_video', 'Werbung (Video)'),
                             ('next_games', 'Naechsten Spiele'),
                             ('next_home_games', 'Naeachsten Heimspiele'),

                             ]

    content_type = models.CharField(max_length=255, choices=POSSIBLE_CONTENT_TYPE)
    # content = models.ForeignObject(null=True)
    content_path = models.TextField(null=True, blank=True)

    is_visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)


class Presentation(models.Model):
    team = models.ForeignKey(Team)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    displayed = models.BooleanField(default=True)

    def __str__(self):
        return 'Presentation {0} of team {1}'.format(
            self.name,
            str(self.team)
        )

    def get_all_slides(self):
        return Slide.objects.filter(club=self.team.parent_club)

    def get_fields(self):
        return PlayingField.objects.filter()


class PresentationSlideTeam(models.Model):

    presentation = models.ForeignKey(Presentation)
    slide = models.ForeignKey(Slide)

    slide_number = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)



