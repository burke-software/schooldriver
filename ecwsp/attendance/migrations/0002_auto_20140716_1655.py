# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140716_1655'),
        ('attendance', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancelog',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendancelog',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AttendanceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'"Present" will not be saved but may show as a teacher option.', unique=True, max_length=255)),
                ('code', models.CharField(help_text=b'Short code used on attendance reports. Ex: A might be the code for the name Absent', unique=True, max_length=10)),
                ('teacher_selectable', models.BooleanField(default=False)),
                ('excused', models.BooleanField(default=False)),
                ('absent', models.BooleanField(default=False, help_text=b'Some statistics need to add various types of absent statuses, such as the number in parentheses in daily attendance.')),
                ('tardy', models.BooleanField(default=False, help_text=b'Some statistics need to add various types of tardy statuses, such as the number in parentheses in daily attendance.')),
                ('half', models.BooleanField(default=False, help_text=b'Half attendance when counting. DO NOT check off absent otherwise it will double count!')),
            ],
            options={
                'verbose_name_plural': b'Attendance Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseSectionAttendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('time_in', models.TimeField(null=True, blank=True)),
                ('notes', models.CharField(max_length=500, blank=True)),
                ('course_section', models.ForeignKey(to='schedule.CourseSection')),
                ('period', models.ForeignKey(blank=True, to='schedule.Period', null=True)),
                ('status', models.ForeignKey(to='attendance.AttendanceStatus')),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.datetime.now, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('time', models.TimeField(null=True, blank=True)),
                ('notes', models.CharField(max_length=500, blank=True)),
                ('private_notes', models.CharField(max_length=500, blank=True)),
                ('status', models.ForeignKey(to='attendance.AttendanceStatus')),
                ('student', models.ForeignKey(help_text=b"Start typing a student's first or last name to search", to='sis.Student')),
            ],
            options={
                'ordering': (b'-date', b'student'),
                'permissions': ((b'take_studentattendance', b'Take own student attendance'),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='studentattendance',
            unique_together=set([(b'student', b'date', b'status')]),
        ),
    ]
