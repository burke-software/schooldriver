import sys
import os
import inspect

current_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(current_path)

from fabric.api import local
from fabric.api import run
from fabric.contrib import django

django.settings_module('ecwsp.settings')
from django.conf import settings


def convert_to_south():
    local("./manage.py syncdb")
    # This first!
    local('python manage.py convert_to_south sis')
    for app in settings.INSTALLED_APPS:
        if app not in ['sis'] and 0 == app.find('ecwsp.'):
            _app = app.split('ecwsp.')[1]
            local('python manage.py convert_to_south %s' % _app)