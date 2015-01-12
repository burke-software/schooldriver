# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ecwsp.schedule.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardstudent',
            name='student',
            field=models.ForeignKey(to='sis.Student'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('fullname', models.CharField(unique=True, max_length=255, verbose_name=b'Full Course Name')),
                ('shortname', models.CharField(max_length=255, verbose_name=b'Short Name')),
                ('homeroom', models.BooleanField(default=False, help_text=b'Homerooms can be used for attendance')),
                ('graded', models.BooleanField(default=True, help_text=b'Teachers can submit grades for this course')),
                ('description', models.TextField(blank=True)),
                ('credits', models.DecimalField(default=ecwsp.schedule.models.get_credits_default, help_text=b'Credits affect GPA.', max_digits=5, decimal_places=2)),
                ('level', models.ForeignKey(verbose_name=b'Grade Level', blank=True, to='sis.GradeLevel', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attendance_note', models.CharField(help_text=b'This note will appear when taking attendance.', max_length=255, blank=True)),
                ('cached_grade', models.CharField(verbose_name=b'Final Course Section Grade', max_length=8, editable=False, blank=True)),
                ('grade_recalculation_needed', models.BooleanField(default=True)),
                ('cached_numeric_grade', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('numeric_grade_recalculation_needed', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseMeet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=1, choices=[(b'1', b'Monday'), (b'2', b'Tuesday'), (b'3', b'Wednesday'), (b'4', b'Thursday'), (b'5', b'Friday'), (b'6', b'Saturday'), (b'7', b'Sunday')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255)),
                ('last_grade_submission', models.DateTimeField(blank=True, null=True, editable=False, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('cohorts', models.ManyToManyField(to='sis.Cohort', null=True, blank=True)),
                ('course', models.ForeignKey(to='schedule.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursemeet',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesection',
            name='enrollments',
            field=models.ManyToManyField(to='sis.Student', null=True, through='schedule.CourseEnrollment', blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CourseSectionTeacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_primary', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursesection',
            name='teachers',
            field=models.ManyToManyField(to='sis.Faculty', through='schedule.CourseSectionTeacher', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesectionteacher',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesectionteacher',
            name='teacher',
            field=models.ForeignKey(to='sis.Faculty'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='coursesectionteacher',
            unique_together=set([(b'teacher', b'course_section')]),
        ),
        migrations.CreateModel(
            name='CourseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('is_default', models.BooleanField(default=False, help_text=b'Only one course type can be the default.')),
                ('weight', models.DecimalField(default=1, help_text=b"A course's weight in average calculations is this value multiplied by the number of credits for the course. A course that does not affect averages should have a weight of 0, while an honors course might, for example, have a weight of 1.2.", max_digits=5, decimal_places=2)),
                ('award_credits', models.BooleanField(default=True, help_text=b"When disabled, course will not be included in any student's credit totals. However, the number of credits and weight will still be used when calculating averages.")),
                ('boost', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='course',
            name='course_type',
            field=models.ForeignKey(default=ecwsp.schedule.models.get_course_type_default, to='schedule.CourseType', help_text=b'Should only need adjustment when uncommon calculation methods are used.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='courseenrollment',
            unique_together=set([(b'course_section', b'user')]),
        ),
        migrations.CreateModel(
            name='DaysOff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name=b'Department Name')),
                ('order_rank', models.IntegerField(help_text=b'Rank that courses will show up in reports', null=True, blank=True)),
            ],
            options={
                'ordering': (b'order_rank', b'name'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(blank=True, to='schedule.Department', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='DepartmentGraduationCredits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credits', models.DecimalField(max_digits=5, decimal_places=2)),
                ('class_year', models.ForeignKey(help_text=b'Also applies to subsequent years unless a more recent requirement exists.', to='sis.ClassYear')),
                ('department', models.ForeignKey(to='schedule.Department')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='departmentgraduationcredits',
            unique_together=set([(b'department', b'class_year')]),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursemeet',
            name='location',
            field=models.ForeignKey(blank=True, to='schedule.Location', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='MarkingPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('shortname', models.CharField(max_length=255)),
                ('start_date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('end_date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('grades_due', models.DateField(blank=True, help_text=b'If filled out, teachers will be notified when grades are due.', null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('active', models.BooleanField(default=False, help_text=b'Teachers may only enter grades for active marking periods. There may be more than one active marking period.')),
                ('show_reports', models.BooleanField(default=True, help_text=b'If checked this marking period will show up on reports.')),
                ('school_days', models.IntegerField(help_text=b'If set, this will be the number of days school is in session. If unset, the value is calculated by the days off.', null=True, blank=True)),
                ('weight', models.DecimalField(default=1, help_text=b'Weight for this marking period when calculating grades.', max_digits=5, decimal_places=3)),
                ('monday', models.BooleanField(default=True)),
                ('tuesday', models.BooleanField(default=True)),
                ('wednesday', models.BooleanField(default=True)),
                ('thursday', models.BooleanField(default=True)),
                ('friday', models.BooleanField(default=True)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('school_year', models.ForeignKey(to='sis.SchoolYear')),
            ],
            options={
                'ordering': (b'-start_date',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='daysoff',
            name='marking_period',
            field=models.ForeignKey(to='schedule.MarkingPeriod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesection',
            name='marking_period',
            field=models.ManyToManyField(to='schedule.MarkingPeriod', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='awardstudent',
            name='marking_period',
            field=models.ForeignKey(blank=True, to='schedule.MarkingPeriod', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='OmitCourseGPA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.ForeignKey(to='schedule.Course')),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OmitYearGPA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student', models.ForeignKey(to='sis.Student')),
                ('year', models.ForeignKey(help_text=b'Omit this year from GPA calculations and transcripts.', to='sis.SchoolYear')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            options={
                'ordering': (b'start_time',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursesection',
            name='periods',
            field=models.ManyToManyField(to='schedule.Period', through='schedule.CourseMeet', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursemeet',
            name='period',
            field=models.ForeignKey(to='schedule.Period'),
            preserve_default=True,
        ),
    ]
