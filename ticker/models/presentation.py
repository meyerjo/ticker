from django.db import models

from ticker.models import Club
from ticker.models import PlayingField
from ticker.models import Team


class Slide(models.Model):

    club = models.ForeignKey(Club, on_delete=models.CASCADE)

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

    def __str__(self):
        return 'Slide {0} - {1} - {2} - {3} (Club: {4})'.format(
            self.title,
            self.content_type,
            self.is_visible,
            self.is_deleted,
            self.club.get_name
        )


class Presentation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    displayed = models.BooleanField(default=True)

    def __str__(self):
        return 'Presentation {0} of team {1}'.format(
            self.name,
            self.team
        )

    def get_all_slides_of_club(self):
        return Slide.objects.filter(club=self.team.parent_club)

    def get_fields(self):
        return PlayingField.objects.filter()


class PresentationSlideTeam(models.Model):

    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE)

    slide_number = models.IntegerField()
    slide_visible = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)


    def get_slides(self):
        pass



