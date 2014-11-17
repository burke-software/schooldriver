FROM ubuntu:12.04
ENV PYTHONUNBUFFERED 1

# Basics
RUN apt-get update -qq && apt-get install -y python-psycopg2 libldap2-dev libsasl2-dev libpq-dev postgresql-client git-core python-pip python-dev g++
# Libreoffice
RUN apt-get install -y libreoffice-base-core libreoffice-calc libreoffice-common libreoffice-core libreoffice-emailmerge libreoffice-math libreoffice-style-human libreoffice-writer python-uno
# Supervisor for libreoffice
RUN apt-get install -y supervisor

RUN mkdir -p /tmp/django-sis_libreoffice
ENV HOME /tmp/django-sis_libreoffice
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD dev-requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install -r dev-requirements.txt
ADD . /code/
