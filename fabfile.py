import sys
import os
import inspect
import StringIO

current_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(current_path)

from fabric.api import local, run, sudo, put
from fabric.contrib import django

django.settings_module('ecwsp.settings')
from django.conf import settings

all_instances = ['boston', 'chicago', 'crb', 'crny', 'dbcr', 'demo', 'depaul', 'ndhslaw', 'philly', 'waukegan']

def syncdb():
    for instance in all_instances:
        local('/opt/sword/manage.py syncdb --migrate --settings=%s.settings --pythonpath=/opt/sword/' % instance)

def convert_to_south():
    local("./manage.py syncdb")
    # This first!
    local('python manage.py convert_to_south sis')
    for app in settings.INSTALLED_APPS:
        if app not in ['sis'] and 0 == app.find('ecwsp.'):
            _app = app.split('ecwsp.')[1]
            local('python manage.py convert_to_south %s' % _app)
            
def add_new_celery_user(site_name):
    """ Create a new rabbitmq vhost and celeryd
    """
    local('rabbitmqctl add_user sword_%s sword_%s' % (site_name, site_name))
    local('rabbitmqctl add_vhost sword_%s' % (site_name,))
    local('rabbitmqctl set_permissions -p sword_%s sword_%s ".*" ".*" ".*"' % (site_name, site_name,))
    
    conf_file = """; =======================================
;  celeryd supervisor example for Django
; =======================================
[program:celery_sword_<site>]
command=/opt/sword/manage.py celeryd --autoreload --loglevel=INFO --settings=<site>.settings --pythonpath=/opt/sword/
directory=/opt/sword
user=www-data
numprocs=1
stdout_logfile=/var/log/celeryd.log
stderr_logfile=/var/log/celeryd.log
autostart=true
autorestart=true
startsecs=10
; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600
; if rabbitmq is supervised, set its priority higher
; so it starts first
priority=998
"""
    conf_file = conf_file.replace('<site>',site_name)
    put(StringIO.StringIO(conf_file),'/etc/supervisor/conf.d/celeryd_%s.conf' % (site_name))
    
    beat_conf = """; ==========================================
;  celerybeat supervisor example for Django
; ==========================================

[program:celerybeat_sword_<site>]
command=/opt/sword/manage.py celerybeat --schedule=/var/lib/celery/celerybeat-schedule --loglevel=INFO --settings=<site>.settings --pythonpath=/opt/sword/
directory=/opt/sword/<site>
user=www-data
numprocs=1
stdout_logfile=/var/log/celerybeat.log
stderr_logfile=/var/log/celerybeat.log
autostart=true
autorestart=true
startsecs=10

; if rabbitmq is supervised, set its priority higher
; so it starts first
priority=999"""
    beat_conf = beat_conf.replace('<site>',site_name)
    put(StringIO.StringIO(beat_conf),'/etc/supervisor/conf.d/celerybeat_%s.conf' % (site_name))
    
    
    