=====================
SWoRD Documentation
=====================

:Date: March 29, 2013


Django-sis/SWoRD is an open source school information system built with Django. It relies heavily on the django admin interface for backend usage (registrar, etc.), and is intended for schools with or without work study programs. SWoRD is able to integrate with Naviance Premium Accounts for college preparedness, Engrade for grades, SugarCRM for sales and customer tracking and National Student Clearinghouse for tracking alumni.

In sum, SWoRD includes pluggable apps designed to cover most if not all of a school's needs. The apps include: School Information, Admissions, Alumni, Attendance, Discipline, Schedules/Courses/Grades, Volunteer Tracking, and Work-Study.

.. contents:: Table of Contents
=========================================
Developer/Administrator Information 
=========================================
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

User Permissions
---------------------
SWoRD allows administrators to control individual user permissions. To simplify this process, SWoRD groups individual permissions into larger groups where the administrator can designate accordingly. Some of the aforementioned groups are as follows, with a brief overview:

**Teachers**: users with this designation can create tests, view students, enter grades and take attendance

**Counseling**: allows users to record student meetings, refer students, list a follow up action

**Faculty**: can view alumni, students, and mentoring information

**Work Study**: controls all facets of work-study, including: work_study attendance, fees, visits, companies, payment options, contact supervisors, time sheets, surveys, assign work teams and work team users.

**Registrar**: edit templates, view applicants, edit admissions, view/edit attendance, add custom fields, sync endgrade courses, create schedules, reports, transcript notes and school years

**Volunteer**: add/change/delete volunteer hours, sites, supervisors and student volunteers


It is possible to assign individual user permissions that are found in one group, and assign it to an individual user that only has permissions from another group. For example, you can assign a teacher (who only has teacher permissions) the ability to view a student's counseling records or work study information. This allows school administrators to create unique users with flexible permissions. Further, administrators can create super users who have all permissions from each group. 


Configurations
---------------
SWoRD contains a number of configurations built in that are created with each new instance. 


=====================
SWoRD Apps
=====================

Admissions
----------
The admissions module allows schools to keep track of applicants, and where they are in the application process. Each step in the application process can be customized to fit a school's unique need. Users can designate steps that need to be completed before moving onto the next level. Additionally, SWoRD will track any open houses a student has attended and how the student heard about the school. 


The image above details the dashboard that an admissions counselor or designated user will see when they select the admissions module. Most modules do include a dashboard for the purpose of providing users a general overview of information that is able to be filtered. 

Adding an Applicant
--------------------
To add an applicant: 
1.Select "Applicants" under the Admissions module
2.Enter information about the applicant accordingly. First and Last Name fields are required.
3.Click "save"

SWoRD will then return you to the applicants dashboard where you will see your newly created applicant at the top.

Admissions Levels
------------------
SWoRD allows schools to control admissions levels/steps that are unique to their school process. Appropiately, each step is customizable. To customize these levels:

1.Select "Admissions Levels" under the Admissions module.
2.You will see the screen shown below.
(PIC)
3. From this screen, you can add an admissions level, selecting the "Add Amissions Level" button, or edit an existing one by selecting 'edit' located next the level you are altering. From the edit screen or add screen, make the necessary changes/additions then select save.

The section under the header, "Items needed to be completed to attain this level in the process" refers to creating a checklist of various tasks the applicant may need to complete prior to reaching a new step. For reference, the image below details a checklist containing two required tasks (open house, requested more information) to be completed before the applicant reaches the level of Inquiry. 
(PIC)

Users may assign designated levels to be required in order to advance to the next. For example, schools may deem it required for an applicant to pay an initial deposit prior to registration.

To make a step required, simply check the box found under the "Required" column.



