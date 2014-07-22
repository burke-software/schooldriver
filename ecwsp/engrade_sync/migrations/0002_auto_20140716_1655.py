# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20140716_1655'),
        ('engrade_sync', '0001_initial'),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursesectionsync',
            name='course_section',
            field=models.ForeignKey(to='schedule.CourseSection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesectionsync',
            name='marking_period',
            field=models.ForeignKey(to='schedule.MarkingPeriod'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='coursesectionsync',
            unique_together=set([(b'course_section', b'marking_period')]),
        ),
        migrations.CreateModel(
            name='TeacherSync',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('engrade_teacher_id', models.BigIntegerField(unique=True)),
                ('teacher', models.ForeignKey(to='sis.Faculty', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
