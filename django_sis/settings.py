import os, sys, logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static_files/'),
    ('gumby_css', os.path.join(BASE_DIR, 'components/css/')),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
CKEDITOR_UPLOAD_PATH = os.path.join(BASE_DIR, 'media/uploads')
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components/')

# Django stuff
LOGIN_REDIRECT_URL = "/"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'docker',
        'USER': 'docker',
        'PASSWORD': 'docker',
        'HOST': os.environ.get('DB_1_PORT_5432_TCP_ADDR'),
        'PORT': os.environ.get('DB_1_PORT_5432_TCP_PORT'),
    }
}
EMAIL_HOST = 'daphne.cristoreyny.org'
# Prefered file format, may be changed in user preferences.
# Default o
# o = Open Document
# m = Microsoft Binary
# x = Microsoft XML
PREFERED_FORMAT = 'o'
TIME_ZONE = 'America/New_York'
TIME_INPUT_FORMATS = ('%I:%M %p', '%I:%M%p', '%H:%M:%S', '%H:%M')
TIME_FORMAT = 'h:i A'
DATE_INPUT_FORMATS = ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y','%b. %d, %Y')
DATE_FORMAT = 'M j, Y'
BASE_URL = "http://localhost:8000"

# Global date validators, to help prevent data entry errors
import datetime
from django.core.validators import MinValueValidator # Could use MaxValueValidator too
DATE_VALIDATORS=[MinValueValidator(datetime.date(1970,1,1))] # Unix epoch!

USE_L10N = False
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
  ('es', 'Spanish'),
  ('en', 'English'),
)
SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
USE_I18N = True
SECRET_KEY = '4@=mqjpx*f$3m(1-wl6&02p#cx@*dz4_t26lu@@pmd^2%+)**y'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'apptemplates.Loader',
    'django.template.loaders.eggs.Loader',
)
ROOT_URLCONF = 'django_sis.urls'
WSGI_APPLICATION = 'ecwsp.wsgi.application'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'ecwsp.sis.disable.DisableCSRF',
    )
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'ecwsp.sis.context_processors.global_stuff',
    'django.core.context_processors.static',
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)
#STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
#STATICFILES_STORAGE = 'ecwsp.storage.LessObnoxiousCachedStaticFilesStorage'

DEBUG = True
TEMPLATE_DEBUG = True
AUTH_PROFILE_MODULE = 'sis.UserPreference'

#BOWER
BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-ui',
    'gumby',
    'jquery-migrate',
    'blockui',
    'jquery-color',
    'angular-route',
    'angular-ui-handsontable',
    'underscore',
    'restangular',
    'bootstrap-sass-official',
    'bootstrap-hover-dropdown',
    'angular-ui-bootstrap',
)

#GRAPPELLI
ADMIN_TOOLS_MENU = 'ecwsp.menu.CustomMenu'
ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"
GRAPPELLI_INDEX_DASHBOARD = 'ecwsp.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = '<img src="/static/images/logo.png"/ style="height: 30px; margin-left: -10px; margin-top: -8px; margin-bottom: -11px;">'


AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

#LDAP
LDAP = False
if LDAP:
    LDAP_SERVER = 'admin.example.org'
    NT4_DOMAIN = 'ADMIN'
    LDAP_PORT = 389
    LDAP_URL = 'ldap://%s:%s' % (LDAP_SERVER, LDAP_PORT)
    SEARCH_DN = 'DC=admin,DC=example,DC=org'
    SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName','memberOf', 'cn']
    BIND_USER = 'ldap'
    BIND_PASSWORD = ''
    AUTHENTICATION_BACKENDS += ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',)

#Google Apps
GAPPS = False
if GAPPS:
    GAPPS_DOMAIN = ''
    GAPPS_USERNAME = ''
    GAPPS_PASSWORD = ''
    GAPPS_ALWAY_ADD_GROUPS = False
    AUTHENTICATION_BACKENDS += ('ecwsp.google_auth.backends.GoogleAppsBackend',)

AUTHENTICATION_BACKENDS += ('django_su.backends.SuBackend',)

#CKEDITOR
CKEDITOR_MEDIA_PREFIX = "/static/ckeditor/"
CKEDITOR_UPLOAD_PATH = MEDIA_ROOT + "uploads"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            [ 'Bold', 'Italic', 'Underline', 'Subscript','Superscript',
              '-', 'Image', 'Link', 'Unlink', 'SpecialChar', 'equation',
              '-', 'Format',
              '-', 'Maximize',
              '-', 'Table',
              '-', 'BulletedList', 'NumberedList',
              '-', 'PasteText','PasteFromWord',
            ]
        ],
        'height': 120,
        'width': 640,
        'disableNativeSpellChecker': False,
        'removePlugins': 'scayt,menubutton,contextmenu,liststyle,tabletools,tableresize,elementspath',
        'resize_enabled': False,
        'extraPlugins': 'equation',
    },
}

# LOGGING
# Ignore this stupid error, why would anyone EVER want to know
# when a user cancels a request?
from django.http import UnreadablePostError

def skip_unreadable_post(record):
    if record.exc_info:
        exc_type, exc_value = record.exc_info[:2]
        if isinstance(exc_value, UnreadablePostError):
            return False
    return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'supress_unreadable_post': {
            '()': 'common.logging.SuppressUnreadablePost',
         }
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'filters': ['supress_unreadable_post'],
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['supress_unreadable_post'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}


#Engrade
# http://ww7.engrade.com/api/key.php
ENGRADE_APIKEY = ''
ENGRADE_LOGIN = ''
ENGRADE_PASSWORD = ''
# School UID (admin must be connected to school)
ENGRADE_SCHOOLID = ''


#Naviance
NAVIANCE_ACCOUNT = ''
NAVIANCE_IMPORT_USERNAME = ''
NAVIANCE_USERNAME = ''
NAVIANCE_PASSWORD = ''
# username, id, or unique_id
NAVIANCE_SWORD_ID = 'username'
NAVIANCE_IMPORT_KEY = ''
NAVIANCE_EMAILS = ''

#SchoolReach
SCHOOLREACH_USERID = ''
SCHOOLREACH_PIN = ''
# The id of the list we want to integrate, don't edit this list by hand in SR
SCHOOLREACH_LIST_ID = ''

#Admissions
ADMISSIONS_DEFAULT_COUNTRY = "United States"


#Work Study
MAX_HOURS_DAY = 10
# Sync data to SugarCRM
SYNC_SUGAR = False
SUGAR_URL = ''
SUGAR_USERNAME = ''
SUGAR_PASSWORD = ''
# Strange way of storing routes that Notre Dame High School wanted, default disabled
CRND_ROUTES = False


#Attendance
# Enables option to do course based attendance
# where teacher takes attendance at each course, not just once a day
ATTENDANCE_COURSE_BASED = False


#OMR
QUEXF_URL = ""
QUEXF_DB_NAME = 'quexf'
QUEXF_DB_PASS = ''
QUEXF_DB_USER = ''
QUEXF_DB_HOST = ''


#Canvas LMS
# oauth token, you must make this in Canvas.
# https://canvas.instructure.com/doc/api/file.oauth.html
CANVAS_TOKEN = ''
CANVAS_ACCOUNT_ID = ''
CANVAS_BASE_URL = ''


# django-report-builder
REPORT_BUILDER_GLOBAL_EXPORT = True


# Default apps, settings_local.py will override them.
INSTALLED_APPS = (
    'ecwsp.work_study',
    'ecwsp.engrade_sync',
    'ecwsp.benchmarks',
    'ecwsp.benchmark_grade',
    'ecwsp.naviance_sso',
    'rosetta',
    # These can be enabled if desired but the default is off
    #'ldap_groups',
    #'raven.contrib.django',
    #'ecwsp.integrations.schoolreach',
    #'social.apps.django_app.default',
    #'ecwsp.omr',
    #'ecwsp.integrations.canvas_sync',
    #'django_extensions',
    #'google_auth',
    #'ldap_groups',
)

COMPRESS_PRECOMPILERS = (
   ('text/coffeescript', 'coffee --compile --stdio'),
   ('text/x-scss', 'django_libsass.SassCompiler'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# this will load additional settings from the file settings_local.py
try:
    from settings_server import *
except ImportError:
    print("Warning: Could not import settings_server.py")
try:
    from settings_local import *
except ImportError:
    print("Warning: Could not import settings_local.py")

try:  # prefix cache based on school name to avoid collisions.
    if SCHOOL_NAME and CACHES:
        CACHES['default']['KEY_PREFIX'] = SCHOOL_NAME
except NameError:
    pass # Not using cache

if DEBUG:
    CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

STATICFILES_FINDERS += ('dajaxice.finders.DajaxiceFinder',)
DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = False # Breaks some jquery ajax stuff!

# These are required add ons that we always want to have
INSTALLED_APPS = (
    'autocomplete_light',
    'grappelli.dashboard',
    'grappelli',
    'ecwsp.sis',
    'ecwsp.administration',
    'ecwsp.schedule',
    'ecwsp.admissions',
    'ecwsp.alumni',
    'ecwsp.discipline',
    'ecwsp.attendance',
    'ecwsp.grades',
    'ecwsp.counseling',
    'ecwsp.standard_test',
    'reversion',
    'djcelery',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'localflavor',
    'dajax',
    'dajaxice',
    'ecwsp.volunteer_track',
    'daterange_filter',
    'django_filters',
    'pagination',
    'massadmin',
    'admin_export',
    'custom_field',
    'ckeditor',
    'report_builder',
    'responsive_dashboard',
    'simple_import',
    'djangobower',
    'scaffold_report',
    'django_su',
    'floppy_gumby_forms',
    'floppyforms',
    'widget_tweaks',
    'django_cached_field',
    'rest_framework',
    'api',
    'compressor',
) + INSTALLED_APPS
import django
if django.get_version()[:3] != '1.7':
    INSTALLED_APPS += ('south',)

if 'social.apps.django_app.default' in INSTALLED_APPS:
    TEMPLATE_CONTEXT_PROCESSORS += (
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
    )

if 'ON_HEROKU' in os.environ:
    ON_HEROKU = True
    # Use S3
    INSTALLED_APPS += ('storages', 'collectfast')
    AWS_PRELOAD_METADATA = True
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    COMPRESS_STORAGE = STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    for environment_variable in (
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
    ):
        # Cower, all ye Stack Overflow pedants!
        globals()[environment_variable] = os.environ[environment_variable]
    COMPRESS_URL = STATIC_URL = 'https://{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
    # Use Heroku's DB
    import dj_database_url
    # Use 'local_maroon' as a fallback; useful for testing Heroku config locally
    DATABASES['default'] = dj_database_url.config()

# Keep this *LAST* to avoid overwriting production DBs with test data
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
        'ATOMIC_REQUESTS': True,
    }

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}
