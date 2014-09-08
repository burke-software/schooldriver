#!/bin/bash
export C_FORCE_ROOT="true"
python manage.py celery worker -E -A django_sis --loglevel=INFO &
mkdir -p /tmp/django-sis_libreoffice
export HOME=/tmp/django-sis_libreoffice
/usr/lib/libreoffice/program/soffice.bin --accept='socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' --headless &
sleep 2 && /usr/lib/libreoffice/program/soffice.bin --accept='socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' --headless &
python manage.py runserver_plus 0.0.0.0:8000


