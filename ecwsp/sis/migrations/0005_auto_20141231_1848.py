# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import ecwsp.sis.models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0004_auto_20140717_1638'),
    ]

    operations = [
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
            model_name='cohort',
            name='students',
            field=models.ManyToManyField(to='sis.Student', through='sis.StudentCohort', blank=True),
            preserve_default=True,
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
            name='cohorts',
            field=models.ManyToManyField(to='sis.Cohort', through='sis.StudentCohort', blank=True),
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
    ]
