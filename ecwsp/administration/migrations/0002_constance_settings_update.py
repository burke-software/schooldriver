# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django_sis.settings import CONSTANCE_CONFIG

def configuration_to_constance(apps, schema_editor):
    """adds Configuration object data to Constance Configuration in settings"""
    Configuration = apps.get_model("administration", "Configuration")  
    configs = Configuration.objects.get(name="school pay rate per hour")
    formatted_config = configs.name.replace(" ", "_").upper
    CONSTANCE_CONFIG[formatted_config()] = (configs.value, configs.help_text)

class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(configuration_to_constance),
        ),

        
    ]
