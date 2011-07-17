TEMPLATE_DIRS = ('/home/david/Projects/sword/templates/',)

INSTALLED_APPS = (
    'ajax_select',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'grappelli.dashboard',
    'grappelli',
    'ckeditor',
    'django.contrib.admin',
    'ecwsp.volunteer_track',
    'ecwsp.sis',
    'ecwsp.schedule',
    'ecwsp.work_study',
    'ecwsp.administration',
    'ecwsp.admissions',
    'ecwsp.engrade_sync',
    'ecwsp.alumni',
    'ecwsp.omr',
    'reversion',
    'ldap_groups',
    'django.contrib.webdesign',
    'django_extensions',
    #'debug_toolbar',
)

# http://ww7.engrade.com/api/key.php
ENGRADE_APITKEY = '100000409414915279da7a59f20d985398dd1c29f0788'
# Admin user login
ENGRADE_LOGIN = 'davidburke'
# Engrade password
ENGRADE_PASSWORD = 'engrade77*8'
# School UID (admin must be connected to school)
ENGRADE_SCHOOLID = '1000004094522'