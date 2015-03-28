# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.grades.models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20150316_2148'),
        ('grades', '0002_auto_20150316_2148'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gradecomment',
            options={},
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='finalgrade',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='grade',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='grade',
            name='date_created',
        ),
        migrations.AddField(
            model_name='gradecomment',
            name='enrollment',
            field=models.ForeignKey(default=None, to='schedule.CourseEnrollment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gradecomment',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gradecomment',
            name='comment',
            field=models.CharField(max_length=500, validators=[ecwsp.grades.models.grade_comment_length_validator]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gradecomment',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gradecomment',
            unique_together=set([('enrollment', 'marking_period')]),
        ),
    ]
