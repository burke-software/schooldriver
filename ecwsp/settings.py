#       settings.py
#       
#       Copyright 2010-2011 Burke Software and Consulting LLC
#		Author David M Burke <david@burkesoftware.com>
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

# Single Sign On
CAS = False
if CAS:
    CAS_SERVER_URL = "https://cas.cristoreyny.org:8443/cas/"
    AUTHENTICATION_BACKENDS = ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend','django.contrib.auth.backends.ModelBackend','django_cas.backends.CASBackend',)
elif LDAP:
    AUTHENTICATION_BACKENDS = ('ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend','django.contrib.auth.backends.ModelBackend',)
else:
    AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

LOGIN_REDIRECT_URL = "/"

# Google Apps Settings
GAPPS = False
if GAPPS:
    GAPPS_DOMAIN = ''
    GAPPS_USERNAME = ''
    GAPPS_PASSWORD = ''
    AUTHENTICATION_BACKENDS += ('ecwsp.google_auth.backends.GoogleAppsBackend',)

# admins get emailed if there is an error
ADMINS = (
    ('Admin', 'someone@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sword',
        'USER': 'sword',
        'PASSWORD': '1234',
    }
}

# This section should not normally be edited
MANAGERS = ADMINS

# SMTP server
EMAIL_HOST = 'daphne.cristoreyny.org'

# Max number of hours a student can work per day.
MAX_HOURS_DAY = 10

# Sync data to SugarCRM
SYNC_SUGAR = False

ASP = True

# Prefered file format, may be changed in user preferences.
# Default o
# o = Open Document
# m = Microsoft Binary
# x = Microsoft XML
PREFERED_FORMAT = 'o'
templateHead = os.path.dirname(os.path.abspath(''))
TEMPLATE_DIRS = os.path.join('/opt/sword/templates/')

TIME_ZONE = 'America/New_York'
TIME_INPUT_FORMATS = ('%I:%M %p', '%I:%M%p', '%H:%M:%S', '%H:%M')
TIME_FORMAT = 'h:i A'
DATE_INPUT_FORMATS = ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y')
#USE_L10N = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# base URL
# Example: "www.example.com"
production = False
if production:
    BASE_URL = "http://sis.cristoreyny.org"
else:
    BASE_URL = "http://127.0.0.1:8000"

MEDIA_URL = '/media/'
mediaHead = os.path.dirname(os.path.abspath(''))
MEDIA_ROOT = os.path.join(mediaHead, 'media/')

staticHead = os.path.dirname(os.path.abspath(''))
STATICFILES_DIRS = ((''),
    '/opt/sword/static_files/',
)

staticRootHead = os.path.dirname(os.path.abspath(''))
STATIC_ROOT = os.path.join(staticRootHead, 'static/')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4@=mqjpx*f$3m(1-wl6&02p#cx@*dz4_t26lu@@pmd^2%+)**y'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'django.template.loaders.eggs.load_template_source',
)

ROOT_URLCONF = 'ecwsp.urls'

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'ajax_select',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

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
    'django_filters',
    'pagination',
    'massadmin',
    'admin_export',
    'custom_field',
)

MIDDLEWARE_CLASSES = ()
MIDDLEWARE_CLASSES += (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
if CAS:
    MIDDLEWARE_CLASSES += (
        'django_cas.middleware.CASMiddleware',
        'django.middleware.doc.XViewMiddleware',
        )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    
    'ecwsp.sis.context_processors.global_stuff',
)


AJAX_LOOKUP_CHANNELS = {
    # the simplest case, pass a DICT with the model and field to search against :
    'student' : ('ecwsp.sis.lookups', 'StudentLookup'),
    'all_student' : ('ecwsp.sis.lookups', 'AllStudentLookup'),
    'dstudent' : ('ecwsp.sis.lookups', 'StudentLookupSmall'),
    'studentworker' : ('ecwsp.work_study.lookups', 'StudentLookup'),
    'faculty' : ('ecwsp.sis.lookups', 'FacultyLookup'),
    'faculty_user' : ('ecwsp.sis.lookups', 'FacultyUserLookup'),
    'emergency_contact' : ('ecwsp.sis.lookups', 'EmergencyContactLookup'),
    'discstudent' : ('ecwsp.sis.lookups', 'StudentWithDisciplineLookup'),
    'discipline_view_student': ('ecwsp.sis.lookups', 'DisciplineViewStudentLookup'),
    'attendance_view_student': ('ecwsp.sis.lookups', 'AttendanceStudentLookup'),
    'attendance_quick_view_student': ('ecwsp.sis.lookups', 'AttendanceAddStudentLookup'),
    'volunteer': ('ecwsp.volunteer_track.lookups', 'VolunteerLookup'),
    'site': ('ecwsp.volunteer_track.lookups', 'SiteLookup'),
    'theme': ('ecwsp.omr.lookups', 'ThemeLookup'),
    'company_contact':('ecwsp.work_study.lookups','ContactLookup'),
}

if 'ecwsp.omr' in INSTALLED_APPS:
    AJAX_LOOKUP_CHANNELS['benchmark'] = ('ecwsp.omr.lookups', 'BenchmarkLookup')

DEBUG = True
TEMPLATE_DEBUG = True

AUTH_PROFILE_MODULE = 'sis.UserPreference'

ADMIN_TOOLS_MENU = 'ecwsp.menu.CustomMenu'
GRAPPELLI_INDEX_DASHBOARD = 'ecwsp.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = '<img src="/static/images/logo.png"/ style="height: 30px; margin-left: -10px; margin-top: -8px; margin-bottom: -11px;">'

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
        'height': 80,
        'width': 640,
        'disableNativeSpellChecker': False,
        'removePlugins': 'scayt,menubutton,contextmenu,elementspath',
        'resize_enabled': False,
        'extraPlugins': 'equation',
    },
}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}

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
            'level': 'DEBUG',
            'class': 'raven.contrib.django.handlers.SentryHandler',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# http://ww7.engrade.com/api/key.php
ENGRADE_APIKEY = ''
# Admin user login
ENGRADE_LOGIN = ''
# Engrade password
ENGRADE_PASSWORD = ''
# School UID (admin must be connected to school)
ENGRADE_SCHOOLID = ''

ADMISSIONS_DEFAULT_COUNTRY = "United States"

# URL of master server that stores questions
OMR_MASTER_SERVER='localhost'
# If this instance the master server?
OMR_IS_MASTER_SERVER=True

SENTRY_MAIL_LEVEL = logging.WARNING

# The "new" url path for quexf.
QUEXF_URL = "http://quexf.cristoreyny.org/admin/new.php"

# this will load additional settings from the file settings_local.py
# this is useful when managing multiple sites with different configurations
from settings_local import *
