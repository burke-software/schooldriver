from ecwsp.integrations.schoolreach.views import SchoolReach

from constance import config

from django_sis.celery import app
from ecwsp.sis.helper_functions import all_tenants


@app.task
@all_tenants
def sync_schoolreach_lists():
    """ Email CRA nightly time sheet and student interaction information
    """
    if config.SCHOOLREACH_USERID:
        sr = SchoolReach()
        #sr.update_list()
