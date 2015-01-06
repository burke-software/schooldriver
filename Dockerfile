FROM ubuntu:12.04
ENV PYTHONUNBUFFERED 1

# Basics
RUN apt-get update -qq && apt-get install -y postgresql-client git-core libldap2-dev libsasl2-dev
# Libreoffice
RUN apt-get install -y libreoffice-base-core libreoffice-calc libreoffice-common libreoffice-core libreoffice-math libreoffice-writer python-uno
# Probably can remove this if we use the docker python image and py3
RUN apt-get install -y python-pip python-dev libpq-dev libjpeg-dev g++
# Supervisor for libreoffice
RUN apt-get install -y supervisor

RUN mkdir -p /tmp/django-sis_libreoffice
ENV HOME /tmp/django-sis_libreoffice
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /code
WORKDIR /code
ADD core-requirements.txt /code/
RUN pip install -r core-requirements.txt
ADD dev-requirements.txt /code/
RUN pip install -r dev-requirements.txt
ADD requirements.txt /code/
RUN pip install -r requirements.txt
