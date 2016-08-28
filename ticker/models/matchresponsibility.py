from django.db import models
from django.db.models import CASCADE

from ticker.models import Match
from ticker.models import Profile


class MatchResponsibility(models.Model):

    match = models.ForeignKey(Match, CASCADE)

    profile = models.ForeignKey(Profile, CASCADE)

    time_taken_responsibility = models.DateTimeField(auto_now_add=True)

    time_revoked_responsibilty = models.DateTimeField(default=None)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return 'User {0} has responsibility for match {1} ({2})'.format(
            self.profile.user,
            self.match,
            'active' if self.is_active else 'non-active'
        )
