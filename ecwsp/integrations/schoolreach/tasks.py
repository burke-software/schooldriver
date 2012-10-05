from ecwsp.integrations.schoolreach.views import SchoolReach

from django.conf import settings

from celery.task.schedules import crontab
from celery.decorators import periodic_task

import sys

if 'ecwsp.integrations.schoolreach' in settings.INSTALLED_APPS and settings.SCHOOLREACH_USERID:
    @periodic_task(run_every=crontab(hour=21, minute=47))
    def sync_schoolreach_lists():
        """ Email CRA nightly time sheet and student interaction information
        """
        sr = SchoolReach()
        #sr.update_list()