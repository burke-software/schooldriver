# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.grades_new.models
import ecwsp.sis.constants


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20150102_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('grade', ecwsp.sis.constants.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('comment', models.CharField(blank=True, max_length=500, validators=[ecwsp.grades_new.models.grade_comment_length_validator])),
                ('enrollment', models.ForeignKey(to='schedule.CourseEnrollment', unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('grade', ecwsp.sis.constants.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
                ('comment', models.CharField(blank=True, max_length=500, validators=[ecwsp.grades_new.models.grade_comment_length_validator])),
                ('enrollment', models.ForeignKey(to='schedule.CourseEnrollment')),
            ],
            options={
                'permissions': (('change_own_grade', 'Change grades for own class'), ('change_own_final_grade', 'Change final YTD grades for own class')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeComment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('comment', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ('id',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LetterGradeChoices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('letter', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='grade',
            name='letter_grade',
            field=models.ForeignKey(blank=True, to='grades_new.LetterGradeChoices', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grade',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('enrollment', 'marking_period')]),
        ),
        migrations.AddField(
            model_name='finalgrade',
            name='letter_grade',
            field=models.ForeignKey(blank=True, to='grades_new.LetterGradeChoices', null=True),
            preserve_default=True,
        ),
    ]
