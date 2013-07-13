#       settings.py
#       
#       Copyright 2010-2011 Burke Software and Consulting LLC
#       Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import os,sys, logging

# PATHS
from os.path import join, abspath, dirname
here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..",)
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

TEMPLATE_DIRS = root('templates/')
STATICFILES_DIRS = ((''),
    root('static_files/'),
)
STATIC_ROOT = root('static/')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = root('media/')
CKEDITOR_UPLOAD_PATH = root('media/uploads')


# Django stuff
LOGIN_REDIRECT_URL = "/"
ADMINS = (
    ('Admin', 'someone@example.com'),
)
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sword',
        'USER': 'sword',
        'PASSWORD': '1234',
        'HOST': 'localhost', 
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sword',
        'USER': 'sword',
        'PASSWORD': '1234',
        'HOST': 'localhost', 
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
DATE_FORMAT = 'b. d, Y'
BASE_URL = "http://localhost:8000"

# Global date validators, to help prevent data entry errors
import datetime
from django.core.validators import MinValueValidator # Could use MaxValueValidator too
DATE_VALIDATORS=[MinValueValidator(datetime.date(1970,1,1))] # Unix epoch!

USE_L10N = True
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

""" Optional these you can copy into settings_local
Required apps are towards the bottom of this file (which get added after local 
settings) """
INSTALLED_APPS = (
    #'ecwsp.naviance_sso',
    'ecwsp.work_study',
    'ecwsp.engrade_sync',
    'ecwsp.benchmarks',
    'ecwsp.omr',
    'ecwsp.integrations.canvas_sync',
    #'django_extensions',
    #'google_auth',
    #'ldap_groups',
    'rosetta-grappelli',
    'rosetta',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'pagination.middleware.PaginationMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
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
)
DEBUG = True
TEMPLATE_DEBUG = True
AUTH_PROFILE_MODULE = 'sis.UserPreference'


#GRAPPELLI
ADMIN_TOOLS_MENU = 'ecwsp.menu.CustomMenu'
ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"
GRAPPELLI_INDEX_DASHBOARD = 'ecwsp.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = '<img src="/static/images/logo.png"/ style="height: 30px; margin-left: -10px; margin-top: -8px; margin-bottom: -11px;">'


#LDAP
LDAP = False
if LDAP:
    LDAP_SERVER = 'crnyhs-dc.admin.cristoreyny.org'
    NT4_DOMAIN = 'ADMIN'
    LDAP_PORT = 389
    LDAP_URL = 'ldap://%s:%s' % (LDAP_SERVER, LDAP_PORT)
    SEARCH_DN = 'DC=admin,DC=cristoreyny,DC=org'
    SEARCH_FIELDS = ['mail','givenName','sn','sAMAccountName','memberOf', 'cn']
    BIND_USER = 'ldap'
    BIND_PASSWORD = ''


#CAS
CAS = False
if CAS:
    CAS_SERVER_URL = ""
    AUTHENTICATION_BACKENDS = ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend','django.contrib.auth.backends.ModelBackend','cas.backends.CASBackend',)
    MIDDLEWARE_CLASSES += (
        'cas.middleware.CASMiddleware',
        'django.middleware.doc.XViewMiddleware',
        )
elif LDAP:
    AUTHENTICATION_BACKENDS = ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend','django.contrib.auth.backends.ModelBackend',)
else:
    AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
    
    
#Google Apps
GAPPS = False
if GAPPS:
    GAPPS_DOMAIN = ''
    GAPPS_USERNAME = ''
    GAPPS_PASSWORD = ''
    GAPPS_ALWAY_ADD_GROUPS = False
    AUTHENTICATION_BACKENDS += ('ecwsp.google_auth.backends.GoogleAppsBackend',)


#Django AJAX selects
AJAX_LOOKUP_CHANNELS = {
    # the simplest case, pass a DICT with the model and field to search against :
    'student' : ('ecwsp.sis.lookups', 'StudentLookup'),
    'all_student' : ('ecwsp.sis.lookups', 'AllStudentLookup'),
    'dstudent' : ('ecwsp.sis.lookups', 'StudentLookupSmall'),
    'faculty' : ('ecwsp.sis.lookups', 'FacultyLookup'),
    'faculty_user' : ('ecwsp.sis.lookups', 'FacultyUserLookup'),
    'attendance_quick_view_student': ('ecwsp.attendance.lookups', 'AttendanceAddStudentLookup'),
    'emergency_contact' : ('ecwsp.sis.lookups', 'EmergencyContactLookup'),
    'attendance_view_student': ('ecwsp.attendance.lookups', 'AttendanceStudentLookup'),
    'discstudent' : ('ecwsp.discipline.lookups', 'StudentWithDisciplineLookup'),
    'discipline_view_student': ('ecwsp.discipline.lookups', 'DisciplineViewStudentLookup'),
    'volunteer': ('ecwsp.volunteer_track.lookups', 'VolunteerLookup'),
    'site': ('ecwsp.volunteer_track.lookups', 'SiteLookup'),
    'site_supervisor': ('ecwsp.volunteer_track.lookups', 'SiteSupervisorLookup'),
    'theme': ('ecwsp.omr.lookups', 'ThemeLookup'),
    'studentworker' : ('ecwsp.work_study.lookups', 'StudentLookup'),
    'company_contact':('ecwsp.work_study.lookups','ContactLookup'),
    'course': {'model':'schedule.course', 'search_field':'fullname'},
    'day': ('ecwsp.schedule.lookups','DayLookup'),
    'company'  : {'model':'work_study.workteam', 'search_field':'team_name'}
}
if 'ecwsp.omr' in INSTALLED_APPS:
    AJAX_LOOKUP_CHANNELS['benchmark'] = ('ecwsp.omr.lookups', 'BenchmarkLookup')

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


# this will load additional settings from the file settings_local.py
# this is useful when managing multiple sites with different configurations
from settings_local import *

# must do this after importing settings_local
if 'ecwsp.benchmark_grade' in INSTALLED_APPS:
    AJAX_LOOKUP_CHANNELS['refering_course_student'] = ('ecwsp.benchmark_grade.lookups', 'ReferingCourseStudentLookup')
    STATICFILES_FINDERS += ('dajaxice.finders.DajaxiceFinder',) # this breaks collectstatic if added unconditionally
    INSTALLED_APPS += ('dajaxice', 'dajax') # these don't cause harm, but it seems cleaner not to reference them unless necessary

#Celery
if 'djcelery' in INSTALLED_APPS:
    import djcelery
    djcelery.setup_loader()
    #BROKER_URL = 'amqp://guest:guest@localhost:5672/'
    BROKER_HEARTBEAT = 30
    CELERY_IMPORTS = ()
    if "ecwsp.work_study" in INSTALLED_APPS:
        CELERY_IMPORTS += ("ecwsp.work_study.tasks",)
    if "ecwsp.volunteer_track" in INSTALLED_APPS:
        CELERY_IMPORTS += ("ecwsp.volunteer_track.tasks",)
    if "ecwsp.naviance_sso" in INSTALLED_APPS and NAVIANCE_IMPORT_KEY:
        CELERY_IMPORTS += ("ecwsp.naviance_sso.tasks",)
    if "ecwsp.benchmark_grade" in INSTALLED_APPS:
        CELERY_IMPORTS += ("ecwsp.benchmark_grade.tasks",)
    if "ecwsp.admissions" in INSTALLED_APPS:
        CELERY_IMPORTS += ("ecwsp.admissions.tasks",)
    if "ecwsp.integrations.schoolreach" in INSTALLED_APPS:
        CELERY_IMPORTS += ("ecwsp.integrations.schoolreach.tasks",)
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
    CELERY_ENABLE_UTC = False

# These are required add ons that we always want to have
INSTALLED_APPS += (
    'grappelli.dashboard',
    'grappelli',
    'ecwsp.schedule',
    'ecwsp.administration',
    'ecwsp.admissions',
    'ecwsp.alumni',
    'ecwsp.discipline',
    'ecwsp.attendance',
    'ecwsp.grades',
    'ecwsp.counseling',
    'ecwsp.standard_test',
    'ajax_select',
    'reversion',
    'south',
    'djcelery',
    'django.contrib.admin',    
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'ecwsp.volunteer_track',
    'ecwsp.sis',
    'daterange_filter',
    'django_filters',
    'pagination',
    'massadmin',
    'admin_export',
    'custom_field',
    'ckeditor',
    'report_builder',
    #'responsive_dashboard',
    'simple_import',
    'floppyforms',
)

if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
