# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations
from django.conf import settings
import ecwsp.sis.models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0002_percoursesectioncohort'),
        ('database', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            name='GradeScale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeScaleRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_grade', models.DecimalField(max_digits=5, decimal_places=2)),
                ('max_grade', models.DecimalField(max_digits=5, decimal_places=2)),
                ('letter_grade', models.CharField(max_length=50, blank=True)),
                ('numeric_scale', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('grade_scale', models.ForeignKey(to='sis.GradeScale')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gradescalerule',
            unique_together=set([(b'min_grade', b'max_grade', b'grade_scale')]),
        ),
        migrations.AddField(
            model_name='schoolyear',
            name='grade_scale',
            field=models.ForeignKey(blank=True, to='sis.GradeScale', help_text=b'Alternative grade scale such as letter grades or a 4.0 scale', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentCohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('primary', models.BooleanField(default=False)),
                ('cohort', models.ForeignKey(to='sis.Cohort')),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='emergencycontactnumber',
            options={'verbose_name': 'Student Contact Number'},
        ),
        migrations.RemoveField(
            model_name='userpreference',
            name='omr_default_number_answers',
        ),
        migrations.RemoveField(
            model_name='userpreference',
            name='omr_default_point_value',
        ),
        migrations.RemoveField(
            model_name='userpreference',
            name='omr_default_save_question_to_bank',
        ),
        migrations.AlterField(
            model_name='faculty',
            name='user_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='percoursesectioncohort',
            name='cohort_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sis.Cohort'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='cache_cohort',
            field=models.ForeignKey(related_name='cache_cohorts', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='sis.Cohort', help_text=b'Cached primary cohort.', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='family_access_users',
            field=models.ManyToManyField(related_name='+', to='sis.FamilyAccessUser', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='user_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userpreference',
            name='prefered_file_format',
            field=models.CharField(default=ecwsp.sis.models.get_prefered_format, help_text=b'Open Document recommened.', max_length=b'1', choices=[(b'o', b'Open Document Format (.odt, .ods)'), (b'm', b'Microsoft Binary (.doc, .xls)'), (b'x', b'Microsoft Office Open XML (.docx, .xlsx)')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cohort',
            name='students',
            field=models.ManyToManyField(to='sis.Student', through='sis.StudentCohort', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='cohorts',
            field=models.ManyToManyField(to='sis.Cohort', through='sis.StudentCohort', blank=True),
            preserve_default=True,
        ),
    ]
