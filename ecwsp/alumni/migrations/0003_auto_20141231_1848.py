# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alumni', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumni',
            name='college',
            field=models.ForeignKey(related_name='college_student', blank=True, to='alumni.College', null=True),
            preserve_default=True,
        ),
    ]
