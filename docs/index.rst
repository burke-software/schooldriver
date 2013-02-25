=====================
SWoRD Documentation
=====================

.. contents:: Table of Contents


Developer Information
---------------------
Libreoffice on the server
Should be run as an upstart job something like /etc/init/libreoffice.conf

    start on runlevel 2

    exec /usr/lib/libreoffice/program/soffice.bin '-accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' -headless

    respawn
    respawn limit 10 120

Then start with "start libreoffice"
SugarCRM sync
Download the sync module below and install with Sugar's module loader. It just adds a checkbox called SWORD supervisor.

Next run sword_sync.sql, first ensure the database name is correct. You may want to run them one at a time. Test and make sure Sugar and SWORD work contacts sync up.

quexf
------
Send PDF by email
apt-get purge bsd-mailx rmail sendmail sensible-mda sendmail-bin
sendmail-base sendmail-cf sendmail-doc
kill `pidof 'sendmail: MTA: accepting connections'`
rm -r '/var/spool/mqueue-client'
rm -r '/etc/mail'
rm /etc/aliases
apt-get install postfix
# internet site with smarthost
# smtp relay host: smtp.server.com
# procmail was already installed
# DON'T apt-get install uudeview; Debian package is broken
# compile it from source; put the binary in /opt
touch /var/log/procmail.log
chgrp www-data /var/log/procmail.log
chmod g+w /var/log/procmail.log

Create /opt/new-receiver.sh:
#!/bin/bash
# John Milner
# 20120309
if [ `whoami` != 'root' ]
then
echo "Run this script as root, please." >&2
exit 1
fi
if [ $# -ne 1 ]
then
echo "Usage: $0 NEW_SCHOOL_ABBREVIATION" >&2
exit 1
fi 

randomness="`wget --quiet -O - 'http://www.random.org/strings/?num=1&len=10&digits=on&loweralpha=on&unique=on&format=plain&rnd=new'`"
lower="`echo \"$1\" | tr '[A-Z]' '[a-z]'`"
upper="`echo \"$1\" | tr '[a-z]' '[A-Z]'`"
new_user="$lower-$randomness"
adduser --disabled-login --ingroup www-data --gecos "$upper Scanned Form Receiver" "$new_user" >&2
cat <<END > `eval echo "~$new_user/.procmailrc"`
LOGFILE=/var/log/procmail.log
UMASK=027
:0
| /opt/uudeview -i +a -m -p /var/www/quexf_$lower/doc/filled -
END
echo "$new_user@`postconf -h myhostname`"
