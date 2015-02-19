# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from constance import config

def configuration_to_constance(apps, schema_editor):
    """adds Configuration object data to Constance Config in settings"""
    Configuration = apps.get_model("administration", "Configuration")  
    configs = Configuration.objects.filter(name="school pay rate per hour").first()
    print configs
    if configs[0]:
        formatted_config = configs[0].name.replace(" ", "_").upper
        formatted = formatted_config()
        config.name = (configs.value, configs.help_text)
    else:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(configuration_to_constance),

        
    ]
