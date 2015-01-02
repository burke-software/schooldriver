# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_courseenrollment_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='exclude_days',
            field=models.CharField(default='', help_text=b'Student does not need to attend on this day. Note course sections already specify meeting days; this field is for students who have a special reason to be away.', max_length=100, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursesection',
            name='course',
            field=models.ForeignKey(related_name='sections', to='schedule.Course'),
            preserve_default=True,
        ),
    ]
