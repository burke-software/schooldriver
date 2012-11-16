#!/bin/bash

# install everything needed to run this application, start with deb files, should be run as root
apt-get install apache2 mysql-server python-uno python-xlwt python-reportlab python-mysqldb python-ldap python-pip python-feedparser python-xlrd python-mysqldb mysql-client python2.7-dev rabbitmq-server

# Install this if in production
# apt-get install libapache2-mod-wsgi

# now install python libs that aren't in deb
# stable version of ldap-groups may not work with mysql
pip install --upgrade -r install/dependencies.txt

# optional auth related
# pip install django-auth-gapps django_cas

#prepare mysql
echo "enter mysql root password"
mysql -uroot -p -e "create database sword"

echo "Done, you still need to run python manage.py syncdb, and set up a web server"
exit