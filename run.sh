#!/bin/bash
export C_FORCE_ROOT="true"
celery worker -E -A django_sis -B --loglevel=INFO &
supervisord -c /etc/supervisor/supervisord.conf
python manage.py runserver_plus 0.0.0.0:8000


