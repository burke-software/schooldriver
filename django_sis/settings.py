from __future__ import absolute_import
import os, sys, logging
from datetime import timedelta

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

LOGIN_REDIRECT_URL = "/"
MULTI_TENANT = os.getenv('MULTI_TENANT', False)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME', 'postgres'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_ADDR', 'db_1'),
        'PORT': 5432,
        # If a timeout is not specified, psycopg2 will wait forever, and the
        # executing thread will get stuck indefinitely. A bunch of requests
        # during a Postgres disruption would paralyze the server completely.
        'OPTIONS': {'connect_timeout': 15},
    }
}

for environment_variable in (
    'EMAIL_HOST',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
    'EMAIL_PORT',
    'EMAIL_USE_TLS',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_STORAGE_BUCKET_NAME',
    'GOOGLE_ANALYTICS',
    'RAVEN_DSN',
):
    globals()[environment_variable] = os.getenv(environment_variable)

ALLOWED_HOSTS = ['*']
# username, id, or unique_id
NAVIANCE_SWORD_ID = os.getenv('NAVIANCE_SWORD_ID', 'username')

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
INTERNAL_IPS = ('127.0.0.1',)
USE_I18N = True
SECRET_KEY = os.getenv('SECRET_KEY', '4@=mqjpx*f$3m(1-wl6&02p#cx@*dz4_t26lu@@pmd^2%+)**y')
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
    'impersonate.middleware.ImpersonateMiddleware',
    'ecwsp.sis.disable.DisableCSRF',
    'ecwsp.sis.middleware.SocialAuthExceptionMiddleware',
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
    'constance.context_processors.config',
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)

IS_PRODUCTION = os.getenv('IS_PRODUCTION', False)
if IS_PRODUCTION:
    DEBUG = False
else:
    DEBUG = True

DEBUG_TOOLBAR = False  # Set true to enable debug toolbar
TEMPLATE_DEBUG = DEBUG
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
    'angular-cookies',
    'nghandsontable',
    'angular-bootstrap',
    'angular-resource',
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

IMPERSONATE_ALLOW_SUPERUSER = True
IMPERSONATE_REQUIRE_SUPERUSER = True

AUTHENTICATION_BACKENDS = (
    'ecwsp.sis.backends.CaseInsensitiveModelBackend',
)

#LDAP
LDAP = False
LDAP_SERVER = 'admin.example.org'
NT4_DOMAIN = 'ADMIN'
LDAP_PORT = 389
LDAP_URL = 'ldap://%s:%s' % (LDAP_SERVER, LDAP_PORT)
SEARCH_DN = 'DC=admin,DC=example,DC=org'
SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName','memberOf', 'cn']
BIND_USER = 'ldap'
BIND_PASSWORD = ''

#Google Apps
GAPPS = False
if GAPPS:
    GAPPS_DOMAIN = ''
    GAPPS_USERNAME = ''
    GAPPS_PASSWORD = ''
    GAPPS_ALWAY_ADD_GROUPS = False
    AUTHENTICATION_BACKENDS += ('ecwsp.google_auth.backends.GoogleAppsBackend',)


#CKEDITOR
CKEDITOR_MEDIA_PREFIX = "/static/ckeditor/"
CKEDITOR_UPLOAD_PATH = MEDIA_ROOT + "uploads"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            [ 'Bold', 'Italic', 'Underline', 'Subscript','Superscript',
              '-', 'Image', 'Link', 'Unlink', 'SpecialChar',
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
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
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

CELERYD_HIJACK_ROOT_LOGGER=False


# django-report-builder
REPORT_BUILDER_GLOBAL_EXPORT = True
REPORT_BUILDER_ASYNC_REPORT = True


# Default apps, settings_local.py will override them.
INSTALLED_APPS = (
    'ecwsp.work_study',
    'ecwsp.engrade_sync',
    'ecwsp.benchmarks',
    'ecwsp.benchmark_grade',
    'ecwsp.naviance_sso',
    'rosetta',
    # These can be enabled if desired but the default is off
    #'ecwsp.integrations.canvas_sync',
)

COMPRESS_PRECOMPILERS = (
   ('text/coffeescript', 'coffee --compile --stdio'),
   ('text/x-scss', 'django_libsass.SassCompiler'),
)

REDIS_ADDR = os.environ.get('REDIS_1_PORT_6379_TCP_ADDR', 'localhost')
REDIS_PORT = os.environ.get('REDIS_1_PORT_6379_TCP_PORT', '6379')
REDIS_URL = os.environ.get('REDISCLOUD_URL') or 'redis://{}:{}/0'.format(REDIS_ADDR, REDIS_PORT)

from redisify import redisify
if REDIS_URL:
    CACHES = redisify(default=REDIS_URL)
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

BROKER_URL = REDIS_URL
BROKER_TRANSPORT_OPTIONS = {
    'fanout_prefix': True,
    'fanout_patterns': True,
}

CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
    'cache-grades-nightly': {
        'task': 'ecwsp.grades.tasks.build_grade_cache_task',
        'schedule': crontab(hour=23, minute=1),
    },
    'sent-admissions-email': {
        'task': 'ecwsp.admissions.tasks.email_admissions_new_inquiries',
        'schedule': crontab(hour=23, minute=16),
    },
    'naviance-create-students': {
        'task': 'ecwsp.naviance_sso.tasks.create_new_naviance_students',
        'schedule': crontab(hour=23, minute=31),
    },
    'volunteer-emails': {
        'task': 'ecwsp.volunteer_track.tasks.handle',
        'schedule': crontab(hour=23, minute=46),
    },
    'sync_schoolreach': {
        'task': 'ecwsp.integrations.schoolreach.tasks.sync_schoolreach_lists',
        'schedule': crontab(hour=1, minute=0),
    },
    'email_cra_nightly': {
        'task': 'ecwsp.work_study.tasks.email_cra_nightly',
        # MUST complete before midnight! Could be an issue with multiple timezones.
        'schedule': crontab(hour=20, minute=27),
    },
    'update_contacts_from_sugarcrm': {
        'task': 'ecwsp.work_study.tasks.update_contacts_from_sugarcrm',
        'schedule': timedelta(minutes=30),
    },
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET')

# this will load additional settings from the file settings_local.py
try:
    from .settings_server import *
except ImportError:
    print("Warning: Could not import settings_server.py")
try:
    from .settings_local import *
except ImportError:
    print("Warning: Could not import settings_local.py")

try:  # prefix cache based on school name to avoid collisions.
    if SCHOOL_NAME and CACHES:
        CACHES['default']['KEY_PREFIX'] = SCHOOL_NAME
except NameError:
    pass # Not using cache


if RAVEN_DSN:
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    RAVEN_CONFIG = {
        'dsn': RAVEN_DSN,
        'IGNORE_EXCEPTIONS': ['django.http.UnreadablePostError'],
    }


STATICFILES_FINDERS += ('dajaxice.finders.DajaxiceFinder',)
DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = False # Breaks some jquery ajax stuff!

# These are required add ons that we always want to have
SHARED_APPS = ()

SHARED_APPS = SHARED_APPS + (
    #'constance',
    #'constance.backends.database',
    'ecwsp.customers',
    'ecwsp.administration',
    'djcelery',
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.sessions',
)
TENANT_APPS = (
    #'constance',
    #'constance.backends.database',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'autocomplete_light',
    'social.apps.django_app.default',
    'ldap_groups',
    'ecwsp.sis',
    'ecwsp.administration',
    'ecwsp.schedule',
    'ecwsp.admissions',
    'ecwsp.alumni',
    'ecwsp.discipline',
    'ecwsp.attendance',
    'ecwsp.grades_new',
    'ecwsp.gradebook',
    'ecwsp.counseling',
    'ecwsp.standard_test',
    'ecwsp.integrations.schoolreach',
    'reversion',
    'djcelery',
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
    'floppy_gumby_forms',
    'floppyforms',
    'widget_tweaks',
    'django_cached_field',
    'rest_framework',
    'rest_framework_bulk',
    'api',
    'compressor',
    'impersonate',
) + INSTALLED_APPS

INSTALLED_APPS = list(set(SHARED_APPS + TENANT_APPS))
TENANT_MODEL = "customers.Client"
INSTALLED_APPS = [
    'constance',
    'constance.backends.database',
] + INSTALLED_APPS

if DEBUG_TOOLBAR == True:
    INSTALLED_APPS += ('debug_toolbar',)
    INTERNAL_IPS = ['127.0.0.1', '172.17.42.1', '172.17.42.1', '10.0.1.21',]

CONSTANCE_CONFIG = {
    'SCHOOL_NAME': ('Unnamed School', 'School name'),
    'SCHOOL_COLOR': ('', 'hex color code. Ex: $1122FF'),
    'ALLOW_GOOGLE_AUTH': (False, 'Allow users to log in with Google Apps. This requires setting the email field in student and staff.'),
    'GOOGLE_APPS_DOMAIN': ('', 'Used with ALLOW_GOOGLE_AUTH. Google Apps domain to authenticate against. Probably the part after @ on your email address. Example: myschool.com'),
    'LDAP_URL': ('', 'Ex: ldap://admin.example.com:389'),
    'LDAP_NT4_DOMAIN': ('', 'Ex: ADMIN'),
    'LDAP_BIND_USER': ('', 'Ex: ldap_user'),
    'LDAP_BIND_PASSWORD': ('', 'Bind user\'s password'),
    'LDAP_SEARCH_DN': ('', 'DC=admin,DC=example,DC=com'),
    'SET_ALL_TO_PRESENT': (False, 'If set to True, the default course attendance setting will be "present"'),
    'PREFERED_FORMAT': ('o', 'Prefered file format, may be changed in user preferences. o = Open Document Format (odt), m = Microsoft Binary (doc), x = Office Open XML (docx)'),
    'ADMISSIONS_DEFAULT_COUNTRY': ("United States", ''),
    'WORK_STUDY_MAX_HOURS_DAY': (10, 'Number of hours per day a student is able to work'),
    'SUGAR_SYNC': (False, 'Sync with SugarCRM'),
    'SUGAR_URL': ('', 'SugarCRM Domain'),
    'SUGAR_USERNAME': ('', 'SugarCRM Username'),
    'SUGAR_PASSWORD': ('', 'SugarCRM Password'),
    'SUGAR_SYNC_MINUTES': (30, 'SugarCRM sync every X minutes'),
    'LETTER_GRADE_REQUIRED_FOR_PASS': (60, 'Minimum grade required to be considered "passing"'),
    'CRND_ROUTES': (False, 'Alternative way of storing routes that Notre Dame High School uses. Not recommended.'),
    'CANVAS_TOKEN': ('', 'https://canvas.instructure.com/doc/api/file.oauth.html'),
    'CANVAS_ACCOUNT_ID': ('', ''),
    'CANVAS_BASE_URL': ('', ''),
    'ENGRADE_APIKEY': ('', 'Engrade API key'),
    'ENGRADE_LOGIN': ('', 'Engrade log in'),
    'ENGRADE_PASSWORD': ('', 'Engrade password'),
    'ENGRADE_SCHOOLID': ('', 'School UID (admin must be connected to school)'),
    'NAVIANCE_ACCOUNT': ('', ''),
    'NAVIANCE_IMPORT_USERNAME': ('', ''),
    'NAVIANCE_USERNAME': ('', ''),
    'NAVIANCE_PASSWORD': ('', ''),
    'NAVIANCE_SWORD_ID': ('username', 'Username, id, or unique_id'),
    'NAVIANCE_IMPORT_KEY': ('', ''),
    'NAVIANCE_EMAILS': ('', ''),
    'SCHOOLREACH_USERID': ('', ''),
    'SCHOOLREACH_PIN': ('', ''),
    'SCHOOLREACH_LIST_ID': ('',
        "The id of the list we want to integrate, don't edit this list by hand in SR"),
    'TRANSCRIPT_SHOW_INCOMPLETE_COURSES_WITHOUT_GRADE': (False,
        'Normally a incomplete course would not show on a transcript. When this is enabled '\
        'such courses will show - however grades will be blank.'),
    'APPLICANT_EMAIL_ALERT' : (False, "Send email alert on applicant submission"),
    'APPLICANT_EMAIL_ALERT_ADDRESSES' : ('',
        "Email addresses to send alert to; only one email address per line"),
    'FROM_EMAIL_ADDRESS' : ('', "Default email address to use for sending mail"),
    'GRADES_ALLOW_STUDENT_VIEWING': (True, "Allow students to view their grades online"),
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

USE_S3 = False
if 'USE_S3' in os.environ:
    USE_S3 = True

if DEBUG and not USE_S3:
    INSTALLED_APPS += ('django_extensions',)

if LDAP:
    AUTHENTICATION_BACKENDS += ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',)

TEMPLATE_CONTEXT_PROCESSORS += (
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)
AUTHENTICATION_BACKENDS += ('social.backends.google.GoogleOAuth2',)
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'ecwsp.sis.auth.associate_by_email',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
)

if USE_S3:
    # Use S3
    INSTALLED_APPS += ('storages', 'collectfast')
    AWS_PRELOAD_METADATA = True
    AWS_QUERYSTRING_AUTH = False
    DEFAULT_FILE_STORAGE = 'django_sis.s3utils.MediaRootS3BotoStorage'
    COMPRESS_STORAGE = STATICFILES_STORAGE = 'django_sis.s3utils.CachedS3BotoStorage'
    COMPRESS_URL = STATIC_URL = 'https://{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
    MEDIA_URL = STATIC_URL
    # Use Heroku's DB
    #import dj_database_url
    # Use 'local_maroon' as a fallback; useful for testing Heroku config locally
    #DATABASES['default'] = dj_database_url.config()

if MULTI_TENANT:
    DATABASES['default']['ENGINE'] = 'tenant_schemas.postgresql_backend'
    DATABASE_ROUTERS = ('tenant_schemas.routers.TenantSyncRouter',)
    MIDDLEWARE_CLASSES = ('tenant_schemas.middleware.TenantMiddleware',) + MIDDLEWARE_CLASSES
    INSTALLED_APPS = INSTALLED_APPS + ['tenant_schemas',]

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'PAGINATE_BY_PARAM': 'page_size',
}

MIGRATIONS_DISABLED = False
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travisci',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
elif 'test' in sys.argv:
    # Don't take fucking years to run a test
    class DisableMigrations(object):
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return "notmigrations"
    MIGRATION_MODULES = DisableMigrations()
    MIGRATIONS_DISABLED = True
