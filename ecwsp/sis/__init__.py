import logging
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

if not settings.DEBUG:
    call_command('clearsessions')

