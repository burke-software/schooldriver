# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0002_percoursesectioncohort'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolyear',
            name='grade_scale',
            field=models.ForeignKey(blank=True, to='grades.GradeScale', help_text=b'Alternative grade scale such as letter grades or a 4.0 scale', null=True),
            preserve_default=True,
        ),
    ]
