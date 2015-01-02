# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ecwsp.sis.models
import localflavor.us.models
import custom_field.custom_field
import ckeditor.fields
import django.db.models.deletion
from django.conf import settings
import ecwsp.sis.thumbs
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', ecwsp.sis.models.IntegerRangeField(help_text=b'Example 2014', unique=True)),
                ('full_name', models.CharField(help_text=b'Example Class of 2014', max_length=255, blank=True)),
            ],
            options={
                'verbose_name': b'Graduating Class',
                'verbose_name_plural': b'Graduating Classes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('long_name', models.CharField(help_text=b'Optional verbose name', max_length=500, blank=True)),
                ('primary', models.BooleanField(default=False, help_text=b'If set true - all students in this cohort will have it set as primary!')),
            ],
            options={
                'ordering': (b'name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fname', models.CharField(max_length=255, verbose_name=b'First Name')),
                ('mname', models.CharField(max_length=255, null=True, verbose_name=b'Middle Name', blank=True)),
                ('lname', models.CharField(max_length=255, verbose_name=b'Last Name')),
                ('relationship_to_student', models.CharField(max_length=500, blank=True)),
                ('street', models.CharField(help_text=b'Include apt number', max_length=255, null=True, blank=True)),
                ('city', models.CharField(default=ecwsp.sis.models.get_city, max_length=255, null=True, blank=True)),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, null=True, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zip', models.CharField(max_length=10, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('primary_contact', models.BooleanField(default=True, help_text=b'This contact is where mailings should be sent to. In the event of an emergency, this is the person that will be contacted first.')),
                ('emergency_only', models.BooleanField(default=False, help_text=b'Only contact in case of emergency')),
                ('sync_schoolreach', models.BooleanField(default=True, help_text=b'Sync this contact with schoolreach')),
            ],
            options={
                'ordering': (b'primary_contact', b'lname'),
                'verbose_name': b'Student Contact',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmergencyContactNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('ext', models.CharField(max_length=10, null=True, blank=True)),
                ('type', models.CharField(blank=True, max_length=2, choices=[(b'H', b'Home'), (b'C', b'Cell'), (b'W', b'Work'), (b'O', b'Other')])),
                ('note', models.CharField(max_length=255, blank=True)),
                ('primary', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(to='sis.EmergencyContact')),
            ],
            options={
                'verbose_name': b'Student Contact',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('number', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('ext', models.CharField(max_length=10, null=True, blank=True)),
                ('teacher', models.BooleanField(default=False)),
            ],
            options={
                'ordering': (b'last_name', b'first_name'),
                'verbose_name_plural': b'Faculty',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='GradeLevel',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, verbose_name=b'Grade Number', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=150, verbose_name=b'Grade Name')),
            ],
            options={
                'ordering': (b'id',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('iso_code', models.CharField(help_text=b'ISO 639-1 Language code http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes', max_length=2, blank=True)),
                ('default', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageToStudent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', ckeditor.fields.RichTextField(help_text=b'This message will be shown to students when they log in.')),
                ('start_date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('end_date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReasonLeft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('start_date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('end_date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('grad_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('active_year', models.BooleanField(default=False, help_text=b'DANGER!! This is the current school year. There can only be one and setting this will remove it from other years. If you want to change the active year you almost certainly want to click Management, Change School Year.')),
                ('benchmark_grade', models.BooleanField(default=ecwsp.sis.models.get_default_benchmark_grade, help_text=b'Causes additional information to appear on transcripts. The configuration option "Benchmark-based grading" sets the default for this field.')),
            ],
            options={
                'ordering': (b'-start_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('mname', models.CharField(max_length=150, null=True, verbose_name=b'Middle Name', blank=True)),
                ('grad_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('pic', ecwsp.sis.thumbs.ImageWithThumbsField(null=True, upload_to=b'student_pics', blank=True)),
                ('alert', models.CharField(help_text=b'Warn any user who accesses this record with this text', max_length=500, blank=True)),
                ('sex', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('bday', models.DateField(blank=True, null=True, verbose_name=b'Birth Date', validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('date_dismissed', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('unique_id', models.IntegerField(help_text=b'For integration with outside databases', unique=True, null=True, blank=True)),
                ('ssn', models.CharField(max_length=11, null=True, blank=True)),
                ('parent_guardian', models.CharField(max_length=150, editable=False, blank=True)),
                ('street', models.CharField(max_length=150, editable=False, blank=True)),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, null=True, editable=False, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('city', models.CharField(max_length=255, blank=True)),
                ('zip', models.CharField(max_length=10, editable=False, blank=True)),
                ('parent_email', models.EmailField(max_length=75, editable=False, blank=True)),
                ('alt_email', models.EmailField(help_text=b'Alternative student email that is not their school email.', max_length=75, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('individual_education_program', models.BooleanField(default=False)),
                ('cached_gpa', models.DecimalField(null=True, editable=False, max_digits=5, decimal_places=2, blank=True)),
                ('gpa_recalculation_needed', models.BooleanField(default=True)),
            ],
            options={
                'ordering': (b'last_name', b'first_name'),
                'permissions': ((b'view_student', b'View student'), (b'view_ssn_student', b'View student ssn'), (b'view_mentor_student', b'View mentoring information student'), (b'reports', b'View reports')),
            },
            bases=('auth.user', custom_field.custom_field.CustomFieldModel),
        ),
        migrations.AddField(
            model_name='student',
            name='cache_cohort',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='sis.Cohort', help_text=b'Cached primary cohort.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='class_of_year',
            field=models.ForeignKey(verbose_name=b'Graduating Class', blank=True, to='sis.ClassYear', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='emergency_contacts',
            field=models.ManyToManyField(to='sis.EmergencyContact', verbose_name=b'Student Contact', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='family_preferred_language',
            field=models.ForeignKey(default=ecwsp.sis.models.get_default_language, blank=True, to='sis.LanguageChoice', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='reason_left',
            field=models.ForeignKey(blank=True, to='sis.ReasonLeft', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='siblings',
            field=models.ManyToManyField(to='sis.Student', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='student',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Grade level', blank=True, to='sis.GradeLevel', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'student_files')),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentHealthRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('record', models.TextField()),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', localflavor.us.models.PhoneNumberField(max_length=20)),
                ('ext', models.CharField(max_length=10, null=True, blank=True)),
                ('type', models.CharField(blank=True, max_length=2, choices=[(b'H', b'Home'), (b'C', b'Cell'), (b'W', b'Work'), (b'O', b'Other')])),
                ('note', models.CharField(max_length=255, blank=True)),
                ('student', models.ForeignKey(blank=True, to='sis.Student', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TranscriptNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(blank=True)),
                ('student', models.ForeignKey(to='sis.Student')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TranscriptNoteChoices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='transcriptnote',
            name='predefined_note',
            field=models.ForeignKey(blank=True, to='sis.TranscriptNoteChoices', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefered_file_format', models.CharField(default=b'o', help_text=b'Open Document recommened.', max_length=b'1', choices=[(b'o', b'Open Document Format (.odt, .ods)'), (b'm', b'Microsoft Binary (.doc, .xls)'), (b'x', b'Microsoft Office Open XML (.docx, .xlsx)')])),
                ('include_deleted_students', models.BooleanField(default=False, help_text=b'When searching for students, include deleted (previous) students.')),
                ('omr_default_point_value', models.IntegerField(default=1, help_text=b'How many points a new question is worth by default', blank=True)),
                ('omr_default_save_question_to_bank', models.BooleanField(default=False)),
                ('omr_default_number_answers', models.IntegerField(default=2, blank=True)),
                ('gradebook_preference', models.CharField(blank=True, max_length=10, choices=[(b'O', b'Online Gradebook'), (b'S', b'Spreadsheet'), (b'E', b'Engrade'), (b'M', b'Manual')])),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyAccessUser',
            fields=[
            ],
            options={
                'ordering': (b'last_name', b'first_name'),
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='student',
            name='family_access_users',
            field=models.ManyToManyField(to='sis.FamilyAccessUser', blank=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='StudentCourseSection',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('sis.student',),
        ),
    ]
