from __future__ import absolute_import
import os
from django.conf import settings
from django.db import connection

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_sis.settings')

if settings.MULTI_TENANT:
    from tenant_schemas_celery.app import CeleryApp
    app = CeleryApp('django_sis')
else:
    from celery import Celery
    app = Celery('django_sis')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task()
def debug_task():
    print('hey')
    print(connection.schema_name)
    #print('Request: {0!r}'.format(self.request))


