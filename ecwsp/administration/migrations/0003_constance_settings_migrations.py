# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from constance import config
        
def configuration_to_constance(apps, schema_editor):
    """adds Configuration object data to Constance Config in settings"""
    Configuration = apps.get_model("administration", "Configuration")  
    configs = Configuration.objects.filter(name="Default course credits").first()
    if configs:
        formatted_config = config_name.replace(" ", "_").replace("-", "_").upper
        formatted = str(formatted_config())
        setattr(config, formatted, '')
    else:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_constance_settings_update'),
    ]

    operations = [
        migrations.RunPython(configuration_to_constance),

        
    ]
