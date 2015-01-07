# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='enrollment',
            field=models.ForeignKey(blank=True, to='schedule.CourseEnrollment', null=True),
            preserve_default=True,
        ),
    ]
