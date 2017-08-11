# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticker', '0015_auto_20160910_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='presses_json',
            field=models.TextField(default=None, blank=True, null=True),
        ),
    ]
