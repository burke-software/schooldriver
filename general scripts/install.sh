#!/bin/bash

# install everything needed to run this application, start with deb files, should be run as root
apt-get install mysql-server libapache2-mod-wsgi python-xlwt python-reportlab python-mysqldb python-ldap python-pip python-feedparser python-xlrd python-mysqldb mysql-client

# now install python libs that aren't in deb
# stable version of ldap-groups may not work with mysql
pip install django django-reversion simplejson httpagentparser django-ajax-selects django_extensions django-grappelli django-ckeditor elementtree django-filter poster django-ajax-filtered-fields django-mass-edit django-pagination django-admin-export django-custom-field
# optional auth related
pip install django-ldap-groups django-auth-gapps django_cas
#prepare mysql
echo "enter mysql root password"
mysql -uroot -p -e "create database sword"

echo "Done, you still need to run python manage.py syncdb, and set up a web server"
exit
