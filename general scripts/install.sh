#!/bin/bash

# install everything needed to run this application, start with deb files, should be run as root
apt-get install mysql-server python-uno python-xlwt python-reportlab python-mysqldb python-ldap python-pip python-feedparser python-xlrd python-mysqldb mysql-client python2.7-dev rabbitmq-server

# Install this if in production
apt-get install libapache2-mod-wsgi

# now install python libs that aren't in deb
# stable version of ldap-groups may not work with mysql
pip install requests django django-reversion simplejson httpagentparser django-ajax-selects django_extensions django-celery django-grappelli elementtree poster django-ajax-filtered-fields django-mass-edit django-pagination django-admin-export django-custom-field suds

# people don't submit their fixes to pypi so we have to include them
# Django 1.4 compatibility
pip install ../hatchery/django-filter-0.5.3.tar.gz
# Not on pypi
pip install ../hatchery/wojas-django-apptemplates-ce738ccb3f02.tar.gz
# why is this here again?
pip install ../hatchery/django-ckeditor-3.6.2.tar.gz
# pyuno bug related
pip install ../hatchery/South-0.7.5.tar.gz
# Ldap groups won't update to pypi
pip install ../hatchery/django-ldap-groups-0.1.3.tar.gz

# optional auth related
pip install django-auth-gapps django_cas


#prepare mysql
echo "enter mysql root password"
mysql -uroot -p -e "create database sword"

echo "Done, you still need to run python manage.py syncdb, and set up a web server"
exit
