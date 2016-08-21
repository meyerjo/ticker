class League(models.Model):
    name = models.Model(CharField)

    teams = models.Model(ForeignKey(Team))

    def add_team(self):
        pass