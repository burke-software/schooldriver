# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecwsp.grades.models
import ecwsp.sis.constants


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20150316_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('grade', ecwsp.sis.constants.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
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
                ('date_modified', models.DateField(auto_now=True)),
                ('grade', ecwsp.sis.constants.GradeField(null=True, max_digits=8, decimal_places=2, blank=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, validators=[ecwsp.grades.models.grade_comment_length_validator])),
                ('enrollment', models.ForeignKey(to='schedule.CourseEnrollment')),
                ('marking_period', models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LetterGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('letter', models.CharField(max_length=50)),
                ('is_passing', models.BooleanField(default=True, help_text=b'True means this counts as a Passing or 100% grade.')),
                ('affects_grade', models.BooleanField(default=True, help_text=b'True means this has an affect on grade calculations')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gradecomment',
            unique_together=set([('enrollment', 'marking_period')]),
        ),
        migrations.AddField(
            model_name='grade',
            name='letter_grade',
            field=models.ForeignKey(blank=True, to='grades.LetterGrade', null=True),
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
            field=models.ForeignKey(blank=True, to='grades.LetterGrade', null=True),
            preserve_default=True,
        ),
    ]
