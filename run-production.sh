#!/bin/bash
# This is for running multiple commands via docker in production
supervisord -c /etc/supervisor/supervisord.conf
python manage.py celery flower &
gunicorn ecwsp.wsgi --log-file - -b 0.0.0.0:8000 -n dev.schooldriver_org

