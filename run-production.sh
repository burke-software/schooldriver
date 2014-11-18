#!/bin/bash
# This is for running multiple commands via docker in production
supervisord -c /etc/supervisor/supervisord.conf
python manage.py celery flower &
uwsgi --chdir=/code \
    --module=ecwsp.wsgi:application \
    --http-socket=0.0.0.0:8000 \
    --processes=1 \
    --threads=2 \
    --harakiri=300 \
    --max-requests=5000 \
    --vacuum \
    --die-on-term
