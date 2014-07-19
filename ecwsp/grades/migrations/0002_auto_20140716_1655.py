# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140716_1655'),
        ('grades', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grade',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([(b'student', b'course_section', b'marking_period')]),
        ),
        migrations.CreateModel(
            name='GradeComment',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('comment', models.CharField(max_length=500)),
            ],
            options={
                'ordering': (b'id',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentMarkingPeriodGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cached_grade', models.DecimalField(null=True, verbose_name=b'MP Average', max_digits=5, decimal_places=2, blank=True)),
                ('grade_recalculation_needed', models.BooleanField(default=True)),
                ('marking_period', models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True)),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='studentmarkingperiodgrade',
            unique_together=set([(b'student', b'marking_period')]),
        ),
        migrations.CreateModel(
            name='StudentYearGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cached_grade', models.DecimalField(null=True, verbose_name=b'Year average', max_digits=5, decimal_places=2, blank=True)),
                ('grade_recalculation_needed', models.BooleanField(default=True)),
                ('cached_credits', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('credits_recalculation_needed', models.BooleanField(default=True)),
                ('student', models.ForeignKey(to='sis.Student')),
                ('year', models.ForeignKey(to='sis.SchoolYear')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='studentyeargrade',
            unique_together=set([(b'student', b'year')]),
        ),
    ]
