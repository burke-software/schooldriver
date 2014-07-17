# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ckeditor.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sis', '0001_initial'),
        ('counseling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralform',
            name='student',
            field=models.ForeignKey(to='sis.Student'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ReferralReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('category', models.ForeignKey(to='counseling.ReferralCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='referralform',
            name='referral_reasons',
            field=models.ManyToManyField(to='counseling.ReferralReason', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentMeeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('notes', ckeditor.fields.RichTextField(blank=True)),
                ('follow_up_notes', models.CharField(max_length=2024, blank=True)),
                ('file', models.FileField(null=True, upload_to=b'student_meetings', blank=True)),
                ('follow_up_action', models.ForeignKey(blank=True, to='counseling.FollowUpAction', null=True)),
                ('referral_form', models.ForeignKey(blank=True, editable=False, to='counseling.ReferralForm', null=True)),
                ('reported_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('students', models.ManyToManyField(to='sis.Student')),
            ],
            options={
                'ordering': (b'-date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentMeetingCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='studentmeeting',
            name='category',
            field=models.ForeignKey(blank=True, to='counseling.StudentMeetingCategory', null=True),
            preserve_default=True,
        ),
    ]
