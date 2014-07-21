# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
