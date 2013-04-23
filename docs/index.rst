=====================
SWoRD Documentation
=====================

:Date: March 29, 2013

Django-sis/SWoRD, Student Worker Relational Database, is an open source school information system built with Django. It relies heavily on the django admin interface for backend usage (registrar, etc.) and is intended for schools with or without work study programs. SWoRD is able to integrate with Naviance Premium Accounts for college preparedness, Engrade for grades, SugarCRM for sales and customer tracking, and National Student Clearinghouse for tracking alumni.

In sum, SWoRD includes pluggable apps designed to cover most if not all a school's needs. The apps include: School Information, Admissions, Alumni, Attendance, Discipline, Schedules/Courses/Grades, Volunteer Tracking, and Work-Study.

.. contents:: Table of Contents
=========================================
Developer and Administrator Information 
=========================================
**Libreoffice on the server**

Should be run as an upstart job like /etc/init/libreoffice.conf::

    start on runlevel 2

    exec /usr/lib/libreoffice/program/soffice.bin '-accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' -headless

    respawn
    respawn limit 10 120

Then start with "start libreoffice"

**SugarCRM sync**

Download the sync module below and install with Sugar's module loader which adds a checkbox called SWoRD supervisor.

Next run sword_sync.sql. First ensure the database name is correct. You may want to run them one at a time. Test and make sure Sugar and SWoRD work contacts sync up.

quexf
------
**Send PDF by email**::

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
SWoRD allows administrators to control individual user permissions. To simplify this process, SWoRD groups individual permissions into larger groups which the administrator can designate accordingly. Some of the groups are as follows:

**Teachers**: Users with this designation may create tests, view students, enter grades, and take attendance.

**Counseling**: record student meetings, refer students, and list follow-up actions

**Faculty**: view alumni, students, and mentoring information

**Work Study**: view work study attendance, fees, visits, companies, payment options, contact supervisors, time sheets, surveys, assign work teams and work team users.

**Registrar**: edit templates, view applicants, edit admissions, view/edit attendance, add custom fields, sync Endgrade courses, create schedules, reports, transcript notes, and school years.

**Volunteer**: add/change/delete volunteer hours, sites, supervisors, and student volunteers


It is possible to assign individual user permissions that are found in one group to an individual user that only has permissions from another group. For example, you can assign a teacher (who only has teacher permissions) the ability to view a student's counseling records or work study information. This allows school administrators to create unique users with flexible permissions. Further, administrators can create superusers who have permissions from all groups. 

Importing Data Into Sword
--------------------------
SWoRD supports the import of data into its database.

In order to make the import process as simple as possible for schools transitioning into SWoRD or schools preparing for the new school year, SWoRD allows data to be imported via Excel or LibreOffice documents.

There are two easy ways to import data, both of which *require* the appropiate permissions for the user. The first method is described below:

1. To access the import screen, select Admin > School import from the navigation menu (located at the top right corner of the SWoRD dashboard).
2. Download the sample data from the **sample data** link available in light blue font. The sample data is a pre-formatted Excel/Office file that shows what can be imported.
3. Follow the outline on the appropiate tab. For example, if importing students, follow the students tab; if importing applicants, follow the applicants tab, etc. 
4. Delete all the other tabs once you've decide what model you are importing so you are left with, for example, only the *students* tab.
5. Enter all information about the student you would like to have imported. **NOTE:** For every tab, a unique ID or student username is required. This allows SWoRD to identify to which student the data is pertinent. If you use unique ID and not a username, SWoRD will automatically generate a username using a combination of the first and last name e.g. for Joe Student, jstudent is generated.
6. Leave blank any columns for which you lack the data or do not wish to import.
7. Save
8. Once saved you may return to the import screen and upload the xls or ods file you have just created.

The follow newer method below allows users to set up an Excel/Open Office document without specifying a tab name or following any specific format in columns.

1. As described above, select Admin > School import from the navigation menu.
2. Select **Click here** located at the very top of this page in blue text, which brings you to an import screen.
3. Enter a name.
4. Select browse to locate your Excel document
5. Under Import type, select from Create New Records, Create and Update Records, and Only Update Records. 
6. Select a Model, which refers to where you are importing the data. Select students for students, applicants for applicants, etc.
7. Click Submit.
8. The next page will verify your column data and allow you to preview and then run the import.

Configurations
---------------
SWoRD contains a number of built-in configurations that are created with each new instance designed to make functions easier to edit or implement. 

For example, in configurations for email in the **How to obtain student email** function, users may designate three values designed to direct SWoRD emails. 
**Append** appends the domain name after a student's username like jstudent@domainname.org. 
**User** takes the email address from the Auth->User record.
**Student** takes the email address marked from the *alt email* field of a student record page. 

Getting Started
----------------

**Server:** SWoRD can be installed in any platform that can run Django. It should be noted, however, that all testing is done in Ubuntu Linux 10.04 with MySQL.

**Client:** SWoRD is divided into two parts: the admin site and the student/company-facing site. The student/company-facing site is tested in Firefox, Chrome, Opera, and IE 6,7,8. The admin site is tested only in standards-compliant browsers such as Firefox, Opera, and Chrome. If using IE, you should install the Chrome Frame add-on.

**Editing Templates** requires Office software. Creating report templates require LibreOffice and *must* be saved in ODT format. Keep in mind that end-users may select their preferred office format preference, so ODT is *not* required to just view a report.

Using the ISO-supported Open Document format is recommended for best inter-operability, however doc and xls binary formats are highly supported. In rare cases, formatting may be slightly different in these formats. Office Open XML, while supported, is *not* recommended. 

Log Entries
--------------
Log entries record all actions completed during a SWoRD's instance. This allows administrators and superusers to locate any changes made at specific dates or times. Admins will see a dashboard similar to what is shown below:

IMAGE

**User** refers to which user made a change.

**Action time** details the date and time when the change was made.

**Content type** is the model on which the change was made, e.g. applicant, student, etc.

**Object repr** assigns a specific name to the content type. For example, if applicant was the content type, then object repr will list an exact name like Joe Student.

**Is Addition, Is Deletion, Is Change**: True/False indicator which shows what type of action was completed.

Similar to other dashboards in SWoRD, users may sort by clicking column headers and using the filter tool.

Templates
------------
All SWoRD instances come packaged with a set of general templates. These templates allow users to generate a number of varied reports, including:Tardy Letters, Daily Attendance, Progress Reports, Transcripts, Travel Maps, Test Results, Discipline Report

A list of all available templates, free to download is found `here
<https://sites.google.com/a/cristoreyny.org/sword-wiki/preparing-for-a-new-school-year/templates>`_.

SWoRD further allows users to create and edit their own templates to be used accordingly and will be discussed in the next section, Report Writing.

Report Writing and Creating Templates
---------------------------------------
**Note** Before you proceed, please be aware that in most cases it's best to simply edit existing templates found in your templates location, rather than creating entirely new templates as this section will discuss. 

SWoRD provides the means for end users to create and utilize their own customized reports/templates. All reports are made using the `Appy Framework
<http://appyframework.org/pod.html>`_.

The basic process works like this: user creates report template in a word processor >>> the template gets uploaded into SWoRD >>> Download/use finished report.

To get started, it is first recommended that you use `LibreOffice
<http://www.libreoffice.org/>`_ with the Insert Field extension found `here
<https://sites.google.com/a/cristoreyny.org/sword-wiki/preparing-for-a-new-school-year/report-writing/insert_field1_1.oxt?attredirects=0>`_.

**Note:** When creating templates, ODT format is *required* and all files must be saved in the .odt extension, which is the default in LibreOffice.

**Note:** Microsoft Office can be used with track changes used to denote fields, however, this method is *not* recommended.

**Note:** All finished reports may be opened with Microsoft Office.

1. When you enter "fields" in Libre, this refers to database fields.
2. Insert field using the insert field extension mentioned above

IMAGE

3. Edit a field by double clicking on one.

*Note:* You can see a list of available fields to choose from by typing this into your SWoRD instance's URL. SAMPLESCHOOLURL/admin/doc/models. Some fields are calculated, for example he_she is based off of the sex of a student. Any type: list field cannot be used directly, but must be placed in a loop.

**Logic in Templates** You may use any Python logic in a template. For example in the above screenshot there is a note "do section for student in students". This logic can technically be placed in a field, however it's easier to read in a note. To create a note click Insert > Comment. In the example a section is being created for each student in the field "students". students is a list of students as defined in "School Reports" in SWORD. To create a section click Insert, Section. In the example the section includes a page break. SWoRD will create a section (page break included) for each student in your list of students. This makes for similar results of a mail merge. You may also "do row" or "do cell" to create tables.

You may even include Django specific code, for example students.filter(fname="Joe") would result in a list of students with the first name of "Joe". For more see`Django's retrieving objects
<https://docs.djangoproject.com/en/dev/topics/db/queries/#retrieving-objects>`_. This may get complex fast, therefore SWORD offers some basic sorting and filtering options for you. See School Reports with SWORD. Essentially School Reports will give you the variable students, with your desired filters. If you selected only one student, you will instead have a "student" variable. From here you usually want some type of logic, such as do section for student in students. 

**Spreadsheet Reports** work differently. You can add additional fields to any student related spreadsheet. Select User Preferences and add additional fields here. These additional fields are defined by an administrator and follow the typical . notation (placement.address gets the address of the placement). The gradebook spreadsheet is a special case and a template can be used here. See the included template called "grade spreadsheet".

**Database Field Names** Click on Documentation, then Models to view various Database models. You can chain them by placing . to any related fields. For example student.placement.address would yield the address of the placement of that student.

Exporting SWoRD data to Excel
-------------------------------
SWoRD allows users to export into Excel any and all data that users have input into their respective SWoRD instance. The process of exporting information is very simple, and detailed below:

    1. Click on any model you want to edit from your SWoRD home dash- ex. students, applicants, student workers, discipline, etc.
    2. This will take you to the basic familiar dashboard for that model.
    3. Click the checkbox next to each student you want to pull info from.
    4. Select the black drop down box located towards the bottom of the page.
    5. Select "export to xls" 
    6. A screen asking what you want to be exported appears- make your selections.
    7. Submit.

IMAGE



====================
Student Information System (SIS)
====================
The SIS is the central module of SWoRD which contains profiles, attendance, discipline, work study, and other details pertaining to the student. For information on admissions, adding students, attendance, and discipline, please follow the pertinent headings. 

=====================
Admissions
=====================

The admissions module allows schools to keep track of applicants, and their status in the application process. Each step in the application process can be customized to fit a school's unique need. Users can designate steps that need to be completed before moving onto the next level. Additionally, SWoRD may track any open houses a student has attended and how the student heard about the school. 


The image above details the dashboard that an admissions counselor or designated user sees when the admissions module is selected. Most modules include a dashboard to provide users a general overview of information that is able to be filtered. 


Adding an Applicant
--------------------
To add an applicant: 

1. Select **Applicants** under the Admissions module.
2. Enter information about the applicant accordingly. First and Last Name fields are required.
3. Click **Save**.

SWoRD will then return you to the applicant's dashboard where you will see your newly-created applicant at the top.


------------------
Admissions Levels
------------------
SWoRD allows schools to control admissions levels/steps that are unique to their process. Each step is customizable as follows:

1. Select **Admissions Levels** under the Admissions module.
2. You will see the screen shown below.

IMAGE

3. From this screen you can add an admissions level, selecting the **Add Amissions Level** button or edit an existing one by selecting *edit* located next the level you are altering. From the edit screen or add screen, make the necessary changes/additions and then select save.

The section under the header, **Items needed to be completed to attain this level in the process**, refers to creating a checklist of various tasks the applicant needs to complete prior to reaching a new step. For example, the image below details a checklist containing the two required tasks 'Open House' and 'Request more information' which must be completed before the applicant reaches the level of Inquiry. 

(PIC)

Users may designate levels required in order to advance. For example, schools may require an applicant pay an initial deposit prior to registration. To make a step required, simply check the box found under the **Required** column and save.

---------------------
Filtering Applicants
---------------------
To maximize organization, efficiency, and promote the ease of collecting various admissions data for report preparation, SWoRD contains several filters and functions accessible through the main applicant page. Each column header in the image below will sort accordingly. For example, clicking on Last Name will filter by last name, application decision by decision, etc. 

(PICTURE)
Alternatively, users may choose from the available filters located directly to the right of the applicant list. The drop down list allows users to select and combine the following filters: school year, level, checklist, ready for export, present school, ethnicity, heard about us, and year. The filter tool will do so in real time, no need to select and save.

---------------------
Exporting Applicants
---------------------
SWoRD allows for easy export into an Excel document for sharing or distribution. After applying filters to applicants, follow the steps below to export into an Excel file.

1. Select each applicant you would like to export or select all by selecting the top left checkbox.
2. Click the drop down menu located on the black toolbar at the bottom of the page.
3. Select **Export to XLS**. A box opens up with options on what to export.
4. Choose Select All to export all information entered for each applicant or check specific boxes.
5. Scroll down and select **Submit**.
6. SWoRD will then open an Excel document.

--------------------
Admission Reports
--------------------
Some basic Admission Reports are available built in to SWoRD that allows users to quickly process statistics based on a school year's applicants. 

1. Under the **Admissions** tab in the navigation bar, select **Reports**.
2. Select a year and click **Process Statistics**.
3. SWoRD will generate an Excel document detailing some basic admission statistics such as number of applicants by grade or number of applicants on a particular level in the process.  

In step 2, another option is to choose **Funnel**, which generates on-screen admissions statistics from each step in the admissions process. The report shows total, current, male/female, and rejected reasons.
(SAMPLE OF REPORT) 

----------------------------
Modifying options - Admission Administration
----------------------------
The remaining selections found under Admission Administration such as feeder schools, ethnicity choices, religion choices, school types, etc., allow the dropdown menu choices to be modified. For example, if a particular religion choice is unavailable in dropdown, click on Religion Choices under Admission administration, then the +Add religion choice button to enter the religion, then Save. The entry is now permanently available in the dropdown menu. 

=======================
Adding Students
=======================

1. From Home, click on **Student** in the top navigation bar and click **Edit**.

image 01

2. On the top right, click the **+ Add student** button.

image 02

3. Enter the student’s Last Name, First Name, and Username, which are required fields, and any additional information including Birth Date, Student Contact, and Notes. Click the **Save** button at the bottom right to complete the input of student information.

image 03

* Use the **Filter** function to filter students by Inactivity, Year classification, or Graduating Year. 

(Image04 of Filter function for Class of 2015)

* Click on the column heading **Year** to sort students by Year classification in ascending or descending order. 

(Image05 of Year sorting)

School Years
-----------------------
The starting, ending, and graduation dates of school years may be stored here. One year may be denoted as the active year, which may be used for calculations such as the number of discipline incidents.

Year Classifications
-----------------------
Year classifications are the various grades SWORD supports and their associated names. The defaults in SWORD are:

- Freshman: 9
- Sophomore: 10
- Junior: 11
- Senior: 12

Cohorts
-----------------------
Cohorts are groupings of students within a school; the registrar may find this tool useful. For example, an "advanced class" cohort may be enrolled in particular classes, and homeroom placements may also be organized using cohorts.

====================
Attendance
====================
SWoRD has a built-in attendance module that allows teachers to record daily attendance. Homerooms must already be in place, which are simply courses that are designated as such. 


Taking Attendance
--------------------
1. Click **Attendance** from the navigation menu.
2. A screen appears with a class list. Teachers can mark all students present by **Set all to Present** or click the dropdown menu to mark individually.

Additional comments may be entered in the **Notes** column.

**Things to keep in mind:**

* If a student is already marked absent before, the teacher will see this. At this point, nothing the teacher does will affect it. Keeping it as absent will not change it. Marking present will also not change anything.

* Teachers are not allowed to edit attendance records.

* If a student is enrolled in two different homerooms and is marked absent in one and present in the other, the student will be considered absent. 

--------------------
Attendance Reports
--------------------
Under **Attendance**(navigation menu) and **Reports** are a number of pre-formatted attendance reports designed to be quickly exported into an Excel or Word document. The available reports are:

**Daily Attendance** This report allows users with permission to generate the daily attendance for all students, separated by grade. In particular, the report displays all *absent* students (not marked Present), reasons, and year classifications. Total absences by year classification are tallied at the bottom.

**Lookup Student** Allows users to look up a student's attendance record. The date/reasons for all absent/tardy/late excused, etc. are reported in a Word document. 

**Perfect Attendance Certificates** For a date range or year, this report generates a Word document with a list of students who have zero absenses and tardies.

**Daily Attendance Stats** For a date range or marking periods, this report generates an Excel document showing the date, number present, number absent, and absent percentage.

**By Student Report** This report generates an Excel document of every enrolled student, displaying a tally of all absences and tardies including type of absence (excused, medical, holiday, religious, etc.).

**Aggregate Report** For a date range or marking period, this report is a combined tally of all absences. An absolute Absent Percentage is also reported.

-------------------
Editing Attendance
-------------------

Users with the proper permissions may be allowed to edit attendance for the entire school. To do so,

1. Select **Attendance** from the navigation menu, then **Edit**. 
2. The Edit screen will display all students who have *not* been marked *Present*; edits/notes may be entered. For example, if the school later receives a doctor's note for an absent student, *Absent* may be switched to *Absent Excused* with a *Doctor Visit* note. 

This dashboard also contains a filter option located to the right of the screen, allowing filtering by date, date range, or attendance status (absent, tardy, absent excused, etc.). 

===================
Discipline
===================

The discipline module tracks a student’s discipline information including infractions, actions to be taken, and the teacher who reported the infraction. Similar to the other modules in SWoRD, discipline reports can be generated and exported into an Excel document. 

View Discipline
-----------------
For fast lookup of a particular student's discipline record:

1. Select **Discipline** from the navigation menu, then **View**. 
2. Begin typing in the name of the student in the text box, and SWoRD will present you with a list of available students as shown below:

PICTURE

3. Once a particular student has been selected, SWoRD will present all discipline information that has been input for the student:

PICTURE

-------------------
Discipline Reports
-------------------

Displine Reports allows users to pull and filter discipline data by action, infraction, time, and minimum number of incidents.

IMAGE

**By Student Report** produces a list of students who have a record of disciplinary action including details about the incident.

**Aggregate Report** generates an Excel document tallying each disciplinary incident.

IMAGE

-------------------
Discipline Actions
-------------------
The link to **Discipline Actions** is located in **Home** under **Discipline**. 

Here disciplinary actions available from the dropdown menu may be modified. 
Clicking **Discipline Actions** presents a list of current discipline actions. To add an action, click **+Add Discipline Action**, enter a new discipline, then Save. 

*Schools beginning to use SWoRD should add all discipline actions that the school currently utilizes.* 

IMAGE
