# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import localflavor.us.models
import ckeditor.fields
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('alumni', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumni',
            name='student',
            field=models.OneToOneField(to='sis.Student'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AlumniAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('note', models.TextField(blank=True)),
                ('date', models.DateField(default=datetime.date.today, null=True, blank=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('alumni', models.ManyToManyField(to='alumni.Alumni', null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlumniEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'Personal', b'Personal'), (b'School', b'School'), (b'Work', b'Work'), (b'Other', b'Other')])),
                ('alumni', models.ForeignKey(to='alumni.Alumni')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlumniNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', ckeditor.fields.RichTextField()),
                ('date', models.DateField(auto_now_add=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('alumni', models.ForeignKey(to='alumni.Alumni')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlumniNoteCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alumninote',
            name='category',
            field=models.ForeignKey(blank=True, to='alumni.AlumniNoteCategory', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='AlumniPhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('type', models.CharField(blank=True, max_length=255, null=True, choices=[(b'H', b'Home'), (b'C', b'Cell'), (b'W', b'Work'), (b'O', b'Other')])),
                ('alumni', models.ForeignKey(to='alumni.Alumni')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlumniStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': [b'name'],
                'verbose_name_plural': b'Alumni Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alumni',
            name='status',
            field=models.ForeignKey(blank=True, to='alumni.AlumniStatus', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('type', models.CharField(blank=True, max_length=60, choices=[(b'Public', b'Public'), (b'Private', b'Private')])),
            ],
            options={
                'ordering': [b'name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alumni',
            name='college',
            field=models.ForeignKey(blank=True, to='alumni.College', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='CollegeEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('program_years', models.CharField(blank=True, max_length=1, null=True, choices=[(b'4', b'4-year or higher institution'), (b'2', b'2-year institution'), (b'L', b'less than 2-year institution')])),
                ('begin', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('end', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('status', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'Full-time'), (b'H', b'Half-time'), (b'L', b'Less than half-time'), (b'A', b'Leave of absence'), (b'W', b'Withdrawn'), (b'D', b'Deceased')])),
                ('graduated', models.BooleanField(default=False)),
                ('graduation_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('degree_title', models.CharField(max_length=255, null=True, blank=True)),
                ('major', models.CharField(max_length=255, null=True, blank=True)),
                ('college_sequence', models.IntegerField(null=True, blank=True)),
                ('alumni', models.ForeignKey(to='alumni.Alumni')),
                ('college', models.ForeignKey(to='alumni.College')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Withdrawl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('semesters', models.DecimalField(help_text=b'Number of semesters/trimesters at this college.', null=True, max_digits=5, decimal_places=3, blank=True)),
                ('from_enrollment', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alumni',
            name='withdrawls',
            field=models.ManyToManyField(to='alumni.College', through='alumni.Withdrawl'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='withdrawl',
            name='alumni',
            field=models.ForeignKey(to='alumni.Alumni'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='withdrawl',
            name='college',
            field=models.ForeignKey(to='alumni.College'),
            preserve_default=True,
        ),
    ]
