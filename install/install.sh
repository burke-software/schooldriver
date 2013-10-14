#!/bin/bash
function pip_version_check()
{
    # jnm 20130107
    local pip_path="$1"
    local minimum_required_version="$2"
    
    local installed_version=$("$pip_path" --version | sed -E 's/^pip ([0-9.]+) from.*$/\1/')
    local IFS='.'
    local -a installed_version_array=($installed_version)
    local -a required_version_array=($minimum_required_version)

    for i in 0 1 2 # array elements: major, minor, revision
    do
        [ -z ${installed_version_array[$i]} ] && installed_version_array[$i]=0
        [ -z ${required_version_array[$i]} ] && required_version_array[$i]=0
        [ ${installed_version_array[$i]} -gt ${required_version_array[$i]} ] && return 0
        [ $? -gt 1 ] && return 2 # invalid input; comparison failed
        [ ${installed_version_array[$i]} -lt ${required_version_array[$i]} ] && return 1
        [ $? -gt 1 ] && return 2 # invalid input; comparison failed
    done
    return 0
}
if ! pip_version_check 'pip' '1.2.1'
then
    echo 'You must have pip >= 1.2.1, which may not be provided by your distribution.'
    echo "If you have already installed your distribution's latest version of pip, try running:"
    echo -e '\tpip install --upgrade pip'
    echo 'as root. Afterwards, you may need to run `hash -d pip` for your shell to recognize'
    echo 'the newly-installed pip executable.'
    exit 1
fi

# install everything needed to run this application, start with deb files, should be run as root
apt-get install apache2 mysql-server python-uno python-reportlab python-mysqldb python-ldap python-pip python-feedparser python-xlrd python-mysqldb mysql-client python2.7-dev

# Install this if in production
# apt-get install libapache2-mod-wsgi

# now install python libs that aren't in deb
# stable version of ldap-groups may not work with mysql
pip install --upgrade -r ../requirements.txt
# optional auth related
# pip install django-auth-gapps django_cas

#prepare mysql
echo "enter mysql root password"
mysql -uroot -p -e "create database sword"

echo "Done, you still need to run python manage.py syncdb, and set up a web server"
exit
