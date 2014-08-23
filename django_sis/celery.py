from __future__ import absolute_import
import os
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_sis.settings')

from tenant_schemas_celery.app import CeleryApp
from django.db import connection

app = CeleryApp('django_sis')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(connection.schema_name)
    print('Request: {0!r}'.format(self.request))


