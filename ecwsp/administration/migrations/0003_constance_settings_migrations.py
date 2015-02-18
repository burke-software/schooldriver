# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from constance import config

def configuration_to_constance(apps, schema_editor):
    """adds Configuration object data to Constance Config in settings"""
    Configuration = apps.get_model("administration", "Configuration")  
    configs = Configuration.objects.filter(name="Default course credits").first()
    formatted_config = configs.name.replace(" ", "_").upper
    config.formatted_config() = (configs.value, configs.help_text)

class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_constance_settings_update'),
    ]

    operations = [
        migrations.RunPython(configuration_to_constance),

        
    ]
