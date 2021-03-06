# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-26 10:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ticker', '0005_auto_20160826_1158'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='season',
        #     name='leagues',
        # ),
        migrations.AlterField(
            model_name='game',
            name='game_type',
            field=models.CharField(choices=[('single', 'Herreneinzel'), ('womansingle', 'Dameneinzel'), ('men_double', 'Herrendoppel'), ('women_double', 'Frauendoppel'), ('mixed', 'Mixed')], max_length=32),
        ),
        migrations.AlterField(
            model_name='game',
            name='player_a',
            field=models.ManyToManyField(blank=True, related_name='player_a', to='ticker.Player'),
        ),
        migrations.AlterField(
            model_name='game',
            name='player_b',
            field=models.ManyToManyField(blank=True, related_name='player_b', to='ticker.Player'),
        ),
        migrations.AlterField(
            model_name='game',
            name='sets',
            field=models.ManyToManyField(blank=True, to='ticker.Set'),
        ),
        migrations.AlterField(
            model_name='season',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 26, 10, 26, 30, 471507, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='season',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 26, 10, 26, 30, 471507, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='set',
            name='points_team_a',
            field=models.ManyToManyField(blank=True, related_name='points_team_a', to='ticker.Point'),
        ),
        migrations.AlterField(
            model_name='set',
            name='points_team_b',
            field=models.ManyToManyField(blank=True, related_name='points_team_b', to='ticker.Point'),
        ),
    ]
