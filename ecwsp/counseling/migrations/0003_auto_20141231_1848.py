# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('counseling', '0002_auto_20140716_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referralform',
            name='classroom_teacher',
            field=models.ForeignKey(related_name='referral_classroom_teacher', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referralform',
            name='student',
            field=models.ForeignKey(related_name='+', to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentmeeting',
            name='students',
            field=models.ManyToManyField(related_name='student_meeting_set', to='sis.Student'),
            preserve_default=True,
        ),
    ]
