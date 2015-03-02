# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from constance import config


def configuration_to_constance(apps, schema_editor):
    """adds Configuration object data to Constance Config in settings"""
    Configuration = apps.get_model("administration", "Configuration")  
    settings_to_migrate = ['Students per FTE', 'work_study message to student missing time sheet', 'admissions_inquiry_form_css', 'admissions_hide_inquiry_grade',
    'Admissions to student also makes student worker', 'admissions_override_year_start', 'work_study_timesheet_initial_time',
    'allow for pay', 'work_study contract number', 'work_study contract complete email message', 'work_study_contract_cc_address',
    'work_study_contract_from_address', 'work_study show comment default', 'Students per FTE', 'Edit all Student Worker Fields',
    'counseling referral notice email to', 'Passing Grade', 'Letter Passing Grade', 'Grade comment length limit', 'Gradebook extra information']
    for each_config in settings_to_migrate:
        configs = Configuration.objects.filter(name=each_config).first()
        if configs:
            config_name = configs.name
            config_value = configs.value
            formatted_config = config_name.replace(" ", "_").replace("-", "_").upper
            formatted = str(formatted_config())
            setattr(config, formatted, '')
        else:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0006_constance_settings_migrations'),
    ]

    operations = [
        migrations.RunPython(configuration_to_constance),

        
    ]
