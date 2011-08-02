#!/bin/bash

# install everything needed to run this application, start with deb files, should be run as root
add-apt-repository ppa:libreoffice/ppa
apt-get update
apt-get install mysql-server libapache2-mod-wsgi python-xlwt libreoffice python-reportlab python-mysqldb python-ldap python-setuptools python-feedparser python-xlrd python-mysqldb mysql-client

# now install python libs that aren't in deb
cd /var/tmp
wget http://downloads.sourceforge.net/project/pyrtf/pyrtf/0.45/PyRTF-0.45.tar.gz
tar -xvf PyRTF-0.45.tar.gz
cd PyRTF-0.45
python setup.py install
easy_install django
easy_install django-reversion
easy_install simplejson
easy_install httpagentparser
# stable version may not work with mysql
easy_install django-ldap-groups
easy_install django_cas
easy_install django-ajax-selects
easy_install django_extensions
easy_install django-grappelli
easy_install django-ckeditor
easy_install elementtree
easy_install poster

#prepare mysql
echo "enter mysql root password"
mysql -uroot -p -e "create database sword"

echo "Done, you still need to install appyframework, django, run python manage.py syncdb, and set up a web server"
exit
