# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
import datetime
import custom_field.custom_field
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('required', models.BooleanField(default=True, help_text=b'When true, applicant cannot meet any level beyond this. When false, applicant can leapfrog check items.')),
            ],
            options={
                'ordering': (b'level', b'name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AdmissionLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, validators=[django.core.validators.RegexValidator(b'^[a-zA-Z0-9- ]*$', message=b'Must be Alphanumeric')])),
                ('order', models.IntegerField(help_text=b'Order in which level appears, 1 being first.', unique=True)),
            ],
            options={
                'ordering': (b'order',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='admissioncheck',
            name='level',
            field=models.ForeignKey(to='admissions.AdmissionLevel'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fname', models.CharField(max_length=255, verbose_name=b'First Name')),
                ('mname', models.CharField(max_length=255, verbose_name=b'Middle Name', blank=True)),
                ('lname', models.CharField(max_length=255, verbose_name=b'Last Name')),
                ('pic', models.ImageField(null=True, upload_to=b'applicant_pics', blank=True)),
                ('sex', models.CharField(blank=True, max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('bday', models.DateField(blank=True, null=True, verbose_name=b'Birth Date', validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('unique_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('street', models.CharField(max_length=150, blank=True)),
                ('city', models.CharField(max_length=360, blank=True)),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zip', models.CharField(max_length=10, blank=True)),
                ('ssn', models.CharField(max_length=11, verbose_name=b'SSN', blank=True)),
                ('parent_email', models.EmailField(max_length=75, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('hs_grad_yr', models.IntegerField(max_length=4, null=True, blank=True)),
                ('elem_grad_yr', models.IntegerField(max_length=4, null=True, blank=True)),
                ('present_school_typed', models.CharField(help_text=b'This is intended for applicants to apply for the school. Administrators should use the above.', max_length=255, blank=True)),
                ('present_school_type_typed', models.CharField(max_length=255, blank=True)),
                ('follow_up_date', models.DateField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('parent_guardian_first_name', models.CharField(max_length=150, blank=True)),
                ('parent_guardian_last_name', models.CharField(max_length=150, blank=True)),
                ('relationship_to_student', models.CharField(max_length=500, blank=True)),
                ('from_online_inquiry', models.BooleanField(default=False)),
                ('ready_for_export', models.BooleanField(default=False)),
                ('total_income', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('adjusted_available_income', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('calculated_payment', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('date_added', models.DateField(auto_now_add=True, null=True, validators=[django.core.validators.MinValueValidator(datetime.date(1970, 1, 1))])),
                ('withdrawn_note', models.CharField(max_length=500, blank=True)),
                ('first_to_college', models.BooleanField(default=False)),
                ('individual_education_plan', models.BooleanField(default=False)),
                ('lives_with', models.CharField(blank=True, max_length=50, choices=[(b'Both Parents', b'Both Parents'), (b'Mother', b'Mother'), (b'Father', b'Father'), (b'Guardian(s)', b'Guardian(s)')])),
            ],
            options={
                'ordering': (b'lname', b'fname'),
            },
            bases=(models.Model, custom_field.custom_field.CustomFieldModel),
        ),
    ]
