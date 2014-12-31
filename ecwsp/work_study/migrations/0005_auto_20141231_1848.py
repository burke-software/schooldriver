# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work_study', '0004_auto_20140720_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compcontract',
            name='payment',
            field=models.ForeignKey(blank=True, to='work_study.PaymentOption', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentinteraction',
            name='preset_comment',
            field=models.ManyToManyField(help_text=b'Double-click on the comment on the left to add or click (+) to add a new comment.', to='work_study.PresetComment', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentinteraction',
            name='student',
            field=models.ManyToManyField(help_text=b'An e-mail will automatically be sent to the CRA of this student if type is mentoring.', related_name='student_interaction_set', to='work_study.StudentWorker', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentworker',
            name='am_route',
            field=models.ForeignKey(related_name='am_student_set', blank=True, to='work_study.StudentWorkerRoute', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentworker',
            name='pm_route',
            field=models.ForeignKey(related_name='pm_student_set', blank=True, to='work_study.StudentWorkerRoute', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentworker',
            name='student_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sis.Student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workteam',
            name='am_transport_group',
            field=models.ForeignKey(related_name='workteamset_dropoff', db_column=b'dropoff_location_id', blank=True, to='work_study.PickupLocation', help_text=b'Group for morning drop-off, can be used for work study attendance.', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workteam',
            name='contacts',
            field=models.ManyToManyField(help_text=b'All contacts at this company. You must select them here in order to select the primary contact for a student.', to='work_study.Contact', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workteam',
            name='login',
            field=models.ManyToManyField(help_text=b'Optional. This creates users with "company" permissions, allowing them to sign into the database to review/approve pending and past time sheets for the assigned workteam.', to='work_study.WorkTeamUser', blank=True),
            preserve_default=True,
        ),
    ]
