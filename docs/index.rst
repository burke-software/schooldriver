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
SWoRD contains a number of configurations built in that are created with each new instance designed to make functions easier to edit/change or implement. One example includes the configurations for email- in the **How to obtain student email** function, users may designate three values designed to direct SWoRD emails. **Append** apends the domain name after a student's username, for example jstudent@yourdomain.org. **User** takes the email address from the Auth->User record, and **Student** takes the email address marked from the *alt email* field of the student record page. 

Getting Started
----------------

**Server:** SWoRD can be installed in any platform that can run Django. It should be noted, however that all testing is done in Ubuntu Linux 10.04 with MySQL.

**Client:** SWoRD is divided into two parts, the admin site and the student/company facing site. The student and company facing site is tested in Firefox, Chrome, Opera, and IE 6,7,8. The admin site is tested only in standards compliant browsers such as Firefox, Opera, and Chrome. If using IE, you should install the Chrome Frame add on. 

**Editing Templates** requires office software. Creating report templates require LibreOffice and *must* be saved in ODT format. Keep in mind end users may select their preferred office format preference, so ODT is **NOT** required to just view a report.

Using the ISO supported Open Document format is recommended for best interoperability, however doc and xls binary formats are highly supported. In rare cases formatting may be slightly different in these formats. Office Open XML while supported, is **not** recommended. 

====================
Student Information System (SIS)
====================
The SIS is the central module of SWORD which contains profiles, attendance, discipline, work study, and other details pertaining to the student. For information on admissions, adding students, attendance, and discipline, please click on the pertinent headings. 

=====================
Admissions
=====================

The admissions module allows schools to keep track of applicants, and where they are in the application process. Each step in the application process can be customized to fit a school's unique need. Users can designate steps that need to be completed before moving onto the next level. Additionally, SWoRD will track any open houses a student has attended and how the student heard about the school. 


The image above details the dashboard that an admissions counselor or designated user will see when they select the admissions module. Most modules do include a dashboard for the purpose of providing users a general overview of information that is able to be filtered. 


Adding an Applicant
--------------------
To add an applicant: 

1. Select **Applicants** under the Admissions module
2. Enter information about the applicant accordingly. First and Last Name fields are required.
3. Click **save**

SWoRD will then return you to the applicants dashboard where you will see your newly created applicant at the top.


------------------
Admissions Levels
------------------
SWoRD allows schools to control admissions levels/steps that are unique to their school process. Appropiately, each step is customizable. To customize these levels:

1. Select **Admissions Levels** under the Admissions module.
2. You will see the screen shown below.

IMAGE

3. From this screen, you can add an admissions level, selecting the **Add Amissions Level** button, or edit an existing one by selecting *edit* located next the level you are altering. From the edit screen or add screen, make the necessary changes/additions then select save.

The section under the header, **Items needed to be completed to attain this level in the process** refers to creating a checklist of various tasks the applicant may need to complete prior to reaching a new step. For reference, the image below details a checklist containing two required tasks (open house, requested more information) to be completed before the applicant reaches the level of Inquiry. 
(PIC)

Users may assign designated levels to be required in order to advance to the next. For example, schools may deem it required for an applicant to pay an initial deposit prior to registration.

To make a step required, simply check the box found under the **Required** column and save.

---------------------
Filtering Applicants
---------------------
To maximize organization, efficiency and promote the ease of collecting various admissions data for report preparation, SWoRD contains a myriad of filters and functions accessible through the main applicant page. Each column header in the image below will sort accordingly. For example, clicking on Last Name will filter by last name, application decision by decision, etc. 

(PICTURE)
Alternatively, for more specific filter choices- users may choose from the available filters located directly to the right of the applicant list on the main applicant page. In sum, the drop down list allows users to select and combine the following filters: school year, level, checklist, ready for export, present school, ethnicity, head about us, and year. The filter tool will do so in real time, no need to select and save.

---------------------
Exporting Applicants
---------------------
SWoRD allows for easy export into an Excel document for sharing/distribution. To export applicants after they have been filtered or not, follow the steps below to export them into an Excel file.

1. Select each applicant you would like to export, or select all by selecting the top left-most box to check every applicant.
2. Click the drop down box located on the black tool bar at the bottom of the page.
3. Select **Export to XLS**
4. A box opens up with options on what to export.
5. Select All to pull all information entered for each applicant, or check specific boxes.
6. Scroll down and select **Submit**
7. SWoRD will then open up an Excel document detailing the specified information.

--------------------
Admission Reports
--------------------
Some basic Admission Reports are available built in to SWoRD that allows users to quickly process statistics based on a school year's applicants. 

1. Under the **Admissions** tab located at the top right of your SWoRD screen, select **Reports**
2. Select whichever year you are generating this report for
3. Click **Process Statistics**

SWoRD will then generate an Excel document detailing some basic admission statistics, such as number of applicants by grade, and number of applicants on a particular level in the process.  

Another available pre-made report is labled as **Funnel**. This report will generate on screen admissions statistics from each step in the admissions process. The report will show total, current, male/female and rejected reasons. A sample of this report is shown below.

To create this funnel, follow the first two steps above, but for step 3 select **Funnel** instead of process statistics. 

----------------------------
Other Admissions Options
----------------------------
The remaining selections found under the main admissions screen: feeder schools, ethnicity choices, religion choices, school types, etc. are there to allow for additional options to be visible from drop down boxes on applicants. For example, if an applicant has applied and his/her religion is not listed, the admissions counselor or worker will select **religion choices**, make their addition, then **save**. Once saved, the new religion choice will be permanently saved in the religion choices drop down box for quick future use. 

=======================
Students
=======================

Adding Students
--------------------
image 01

1. From Home, click on **Student** in the top navigation bar and click **Edit**.

image 02

2. On the top right, click the **+ Add student** button.

image03

3. Enter the student’s Last Name, First Name, and Username, which are required fields, and any additional information including Birth Date, Student Contact, and Notes. Click the **Save** button at the bottom right to complete the input of student information.

**Notes**

* Year classifications are the various grades SWORD supports and their associated names. The defaults in SWORD are:

  - Freshman: 9
  - Sophomore: 10
  - Junior: 11
  - Senior: 12

(Image04 of Filter function for Class of 2015)

* Use the **Filter** function to filter students by Inactivity, Year classification, or Graduating Year. 

(Image05 of Year sorting)

* Click on the column heading **Year** to sort students by Year classification in ascending or descending order. 

====================
Attendance
====================
SWoRD has a built in attendance module that allows teachers to record daily attendance. Attendance requires homerooms to be set up. Homerooms are simply courses that are designated as such. 


Taking Attendance
--------------------
1. Click **Attendance** from the navigation menu
2. Teachers will be presented a screen with a list of students currently in their class
3. Teachers can select to mark all students present by clicking the **Set all to Present** option, or alternatively, teachers can click the drop down box by each student to mark individually.

The **notes** column is a blank box where teachers can enter notes regarding the student's attendance, for example if a student is marked absent, the teacher can indicate in the notes box the reason why said student was absent.

**Things to keep in mind in taking attendance:**

-If a student is already marked absent beforehand, the teacher will see this. At this point, nothing the teacher does will effect it. Keeping it as absent will not change it. Marking present will also not change anything.

-Teachers are not allowed to edit atendance records.

-If two teachers mark the same student absent, it will not be recorded twice. This might happen if a student is enrolled in two different homerooms. If one teacher marks the student absent and the other present, the student will be considered absent. 

--------------------
Attendance Reports
--------------------
Built in to SWoRD are a number of pre-formatted and available attendance reports. The reports are designed to allow for the quick generation of data that a user may need to pull. Below, a list of available reports will be described. 

*All reports are located in the same location and will export into an Excel document or a Word document. To access them, select Attendance from the navigation menu and select Reports.*

**Daily Attendance** This report allows users with permission to generate the daily attendance for all students located in their school, separated by grade. Specifically, the report displays all students not marked Present, so the user who pulls this report will know which student was absent, why, and in what grade that student is in. Additionally, the report will tally the number of students absent by each grade which will be visible towards the bottom of the report. 

**Lookup Student** Allows users to quickly look up a student's attendance record. The user will see the date/reasons for all days that student was marked absent/tardy/late excused, etc. in a Microsoft Word document. 

**Perfect Attendance Certificates** This report will produce a Word document with a list of student names who have zero absenses and tardies for the date range and/or year you set.

**Daily Attendance Stats** Will produce an Excel document showing the date, number present, number absent and absent percentage. Users can select a range of dates or marking periods.

**By Student Report** Produces a detailed Excel document covering every enrolled student, and displaying a tally of all absences and tardies, including what type of absence it was- excused, medical, holiday, religious, etc.

**Aggregate Report** Allows users to see a combined tally of all absences for the school, given a marking period or date range. Additionally, the report will produce an absolute Absent Percentage for the entire school.

-------------------
Editing Attendance
-------------------

Users with the proper permissions may be allowed to edit attendance for the entire school. To do so,

1. Select **Attendance** from the navigation menu
2. Click **Edit** from the drop down

The edit screen will display all students who have been marked anything other than *Present*. Users can then enter or make any edits/notes. For example if a student was marked absent, but the school later received a doctor's note, the user can then switch from *Absent* to *Absent Excused* with a note saying- *Doctor Visit*. 

This dashboard also contains a filter option located to the right of the screen, similar to other dashboards in SWoRD. This filter option allows users on this menu to filter by date or date range, and also by attendance status- absent, tardy, absent excused, etc. 

===================
Discipline
===================

The discipline module tracks a student’s discipline information, including: infractions, actions to be taken, and the teacher who reported the infraction. Similar to the other modules in SWoRD, discipline reports can be generated and exported into an Excel document for convenience. 

View Discipline
-----------------
For fast lookup of a particular student's discipline record, SWoRD allows you to do a quick lookup.
From the Navigation menu located on top of your page, select **Discipline**, then **View**. SWoRD will open a page with a text box. Begin typing in the name of the student you would like to view, and SWoRD will present you with a list of available students, as shown below:

PICTURE

Once the appropiate student has been selected, SWoRD will present all discipline information that has been input for the student:

PICTURE

-------------------
Discipline Reports
-------------------

The Discipline Reports function allows users to pull discipline data, while having the option to filter by action, infraction, time, and minimum number of the previously stated.

IMAGE

**By Student Report** will produce a list of all students who have a record of disciplinary action, including details about the incident- e.g. student broke dress code, had his phone out, etc.

**Aggregate Report** produces an Excel document compiling a tally for each disciplinary incident.

IMAGE
