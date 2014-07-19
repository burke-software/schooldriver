import os
PROJECT_DIR = os.path.dirname(__file__)

STATIC_URL = PROJECT_DIR + '/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb',
        'ATOMIC_REQUESTS': True,
    }
}

from django_sis.settings import *
