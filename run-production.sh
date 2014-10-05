#!/bin/bash
# This is for running multiple commands via docker in production
supervisord -c /etc/supervisor/supervisord.conf
python manage.py celery flower &
newrelic-admin run-program  gunicorn ecwsp.wsgi --threads 5 --workers 2 --log-file - -b 0.0.0.0:8000 -n dev.schooldriver_org

