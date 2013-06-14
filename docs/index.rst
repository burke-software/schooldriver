=====================
SWoRD Documentation
=====================

:Date: March 29, 2013

Django-sis/SWoRD, Student Worker Relational Database, is an open source school information system built with Django. It relies heavily on the django admin interface for backend usage (registrar, etc.) and is intended for schools with or without work study programs. SWoRD is able to integrate with Naviance Premium Accounts for college preparedness, Engrade for grades, SugarCRM for sales and customer tracking, and National Student Clearinghouse for tracking alumni.

In sum, SWoRD includes pluggable apps designed to cover most if not all a school's needs. The apps include: School Information, Admissions, Alumni, Attendance, Discipline, Schedules/Courses/Grades, Volunteer Tracking, and Work-Study.

The purpose of this documentation is to be a user manual for end users. Most features will be highlighted and discussed, along with explanations and how-tos for everyday tasks. If you are a developer more interested in the technical aspects of SWoRD, please refer to our github page.

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

The newer method below allows users to set up an Excel/Open Office document without specifying a tab name or following any specific format in columns.

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

.. image:: /images/logentries.png

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

.. image:: /images/fields.png

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

.. image:: /images/exportoxls.png

Custom Fields
--------------
The custom fields option allows schools additional flexibility with regards to storing additional information to a particular model (student, applicants, student worker, etc.).

Under Admin > Custom Fields, the custom fields creation screen displays:

.. image:: /images/customfield1.png

Required fields:

Name- Refers to the name of the custom field. Note: this name will be visible to other end users

Content Type- Designates which model to affix the custom field to. (Student, Alumni, Applicant, Faculty, etc.)

Field Type- Text, Integer, and Boolean- select the type of custom field.

NB: Boolean refers to a simple checkbox. The box can be checked or unchecked when created based on preference. Leave blank for unchecked and enter "1" for checked under the "Default Value" in the creation screen shown above.



====================
Student Information System (SIS)
====================
The SIS is the central module of SWoRD which contains profiles, attendance, discipline, work study, and other details pertaining to the student. For information on admissions, adding students, attendance, and discipline, please follow the pertinent headings. 

Adding Students
-----------------

1. From Home, click on **Student** in the top navigation bar and click **Edit**.

.. image:: /images/sisadd1.png

2. On the top right, click the **+ Add student** button.

.. image:: /images/sisadd2.png

3. Enter the student’s Last Name, First Name, and Username, which are required fields, and any additional information including Birth Date, Student Contact, and Notes. Click the **Save** button at the bottom right to complete the input of student information.

.. image:: /images/sisadd3entry.png

* Use the **Filter** function to filter students by Inactivity, Year classification, or Graduating Year. 

.. image:: /images/sisadd4filter.png

* Click on the column heading **Year** to sort students by Year classification in ascending or descending order. 

.. image:: /images/sisadd5sorting.png

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





=====================
Admissions
=====================

The admissions module allows schools to keep track of applicants, and their status in the application process. Each step in the application process can be customized to fit a school's unique need. Users can designate steps that need to be completed before moving onto the next level. Additionally, SWoRD may track any open houses a student has attended and how the student heard about the school. 

.. image:: /images/applicantdashboard.png

The image above details the dashboard that an admissions counselor or designated user sees when the admissions module is selected. Most modules include a dashboard to provide users a general overview of information that is able to be filtered. 


Adding an Applicant
--------------------
To add an applicant: 

1. Select **Applicants** under the Admissions module.
2. Enter information about the applicant accordingly. First and Last Name fields are required.
3. Click **Save**.

SWoRD will then return you to the applicant's dashboard where you will see your newly-created applicant at the top.



Admissions Levels
------------------
SWoRD allows schools to control admissions levels/steps that are unique to their process. Each step is customizable as follows:

1. Select **Admissions Levels** under the Admissions module.
2. You will see the screen shown below.

.. image:: /images/admissionslevel1.png

3. From this screen you can add an admissions level, selecting the **Add Amissions Level** button or edit an existing one by selecting *edit* located next the level you are altering. From the edit screen or add screen, make the necessary changes/additions and then select save.

The section under the header, **Items needed to be completed to attain this level in the process**, refers to creating a checklist of various tasks the applicant needs to complete prior to reaching a new step. For example, the image below details a checklist containing the two required tasks 'Open House' and 'Request more information' which must be completed before the applicant reaches the level of Inquiry. 

.. image:: /images/admissionslevel2.png

Users may designate levels required in order to advance. For example, schools may require an applicant pay an initial deposit prior to registration. To make a step required, simply check the box found under the **Required** column and save.


Filtering Applicants
---------------------
To maximize organization, efficiency, and promote the ease of collecting various admissions data for report preparation, SWoRD contains several filters and functions accessible through the main applicant page. Each column header in the image below will sort accordingly. For example, clicking on Last Name will filter by last name, application decision by decision, etc. 

.. image:: /images/applicantsalpha.png
Alternatively, users may choose from the available filters located directly to the right of the applicant list. The drop down list allows users to select and combine the following filters: school year, level, checklist, ready for export, present school, ethnicity, heard about us, and year. The filter tool will do so in real time, no need to select and save.


Exporting Applicants
---------------------
SWoRD allows for easy export into an Excel document for sharing or distribution. After applying filters to applicants, follow the steps below to export into an Excel file.

1. Select each applicant you would like to export or select all by selecting the top left checkbox.
2. Click the drop down menu located on the black toolbar at the bottom of the page.
3. Select **Export to XLS**. A box opens up with options on what to export.
4. Choose Select All to export all information entered for each applicant or check specific boxes.
5. Scroll down and select **Submit**.
6. SWoRD will then open an Excel document.


Admission Reports
--------------------
Some basic Admission Reports are available built in to SWoRD that allows users to quickly process statistics based on a school year's applicants. 

1. Under the **Admissions** tab in the navigation bar, select **Reports**

.. image:: /images/admreports1.png

2. Select a year and click **Process Statistics**.
3. SWoRD will generate an Excel document detailing some basic admission statistics such as number of applicants by grade or number of applicants on a particular level in the process.  

In step 2, another option is to choose **Funnel**, which generates on-screen admissions statistics from each step in the admissions process. The report shows total, current, male/female, and rejected reasons.

.. image:: /images/admfunnel.png


Creating Students from Applicants
-----------------------------------
Prior to beginning a new school year, a school will eventually need to convert the applicants into enrolled students to assign classes, grades, etc. 

**IMPORTANT NOTE:** It is important to keep in mind that the only applicants who will be made into students, are those applicants that have the **Ready for Export** check by their name on the dash. Accordingly, marking students as ready for export should be the absolute final step in the process.

.. image:: /images/admcreatestudents1.png

In the example above, only Michael Testerly and James Monroe will be made into students.

To create students from applicants, follow the steps below:

1. Access the Admissions report screen, by selecting Admissions > Reports from the menu located at the top of your page.
2. Select the appropiate school year.
3. Click the **Create students from applicants** button.

.. image:: /images/admcreatestudents2.png



Modifying options - Admission Administration
---------------------------------------------
The remaining selections found under Admission Administration such as feeder schools, ethnicity choices, religion choices, school types, etc., allow the dropdown menu choices to be modified. For example, if a particular religion choice is unavailable in dropdown, click on Religion Choices under Admission administration, then the +Add religion choice button to enter the religion, then Save. The entry is now permanently available in the dropdown menu. 




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


Attendance Reports
--------------------
Under **Attendance**(navigation menu) and **Reports** are a number of pre-formatted attendance reports designed to be quickly exported into an Excel or Word document. The available reports are:

**Daily Attendance** This report allows users with permission to generate the daily attendance for all students, separated by grade. In particular, the report displays all *absent* students (not marked Present), reasons, and year classifications. Total absences by year classification are tallied at the bottom.

**Lookup Student** Allows users to look up a student's attendance record. The date/reasons for all absent/tardy/late excused, etc. are reported in a Word document. 

**Perfect Attendance Certificates** For a date range or year, this report generates a Word document with a list of students who have zero absenses and tardies.

**Daily Attendance Stats** For a date range or marking periods, this report generates an Excel document showing the date, number present, number absent, and absent percentage.

**By Student Report** This report generates an Excel document of every enrolled student, displaying a tally of all absences and tardies including type of absence (excused, medical, holiday, religious, etc.).

**Aggregate Report** For a date range or marking period, this report is a combined tally of all absences. An absolute Absent Percentage is also reported.


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

.. image:: /images/viewdiscipline.png

3. Once a particular student has been selected, SWoRD will present all discipline information that has been input for the student:

.. image:: /images/viewdiscipline2.png


Discipline Reports
-------------------

Displine Reports allows users to pull and filter discipline data by action, infraction, time, and minimum number of incidents.

IMAGE

**By Student Report** produces a list of students who have a record of disciplinary action including details about the incident.

**Aggregate Report** generates an Excel document tallying each disciplinary incident.

.. image:: /images/disciplineaggregate.png


Discipline Actions
-------------------
The link to **Discipline Actions** is located in **Home** under **Discipline**. 

Here disciplinary actions available from the dropdown menu may be modified. 
Clicking **Discipline Actions** presents a list of current discipline actions. To add an action, click **+Add Discipline Action**, enter a new discipline, then Save. 

*Schools beginning to use SWoRD should add all discipline actions that the school currently utilizes.* 

.. image:: /images/disciplineactions.png


=================
Work Study
=================
The SWoRD work study module allows users to keep track of student worker information, including: detailed company information, work assignments, work attendance, directions, work teams, performance reviews, time sheets and more.

Electronic Time Card System
-----------------------------
At the heart of SWoRD's work-study module is the electronic time card system. The electronic time card system allows the school to keep track of a student's working day, what that student did at work, and how their work supervisor felt the student did on a particular day. Additionally, all time cards created by students will be stored neatly into SWoRD where work-study staff can then filter or create reports accordingly. The basic steps are outlined in the image below:

.. image:: /images/timecardprocess.jpg

SWoRD then stores all timecards in the main timecard dash. Users with access to these stored time sheets are able to view each time sheet’s information including date, hours, student accomplishments, and supervisor comments.


.. image:: /images/timesheetdash.png

Adding a Student Worker
--------------------------
Creating student workers involves creating a student first, then "promoting" them to a student worker as follows.

1. Access the student dash 
by selecting **Student** at the navigation bar, then **EDIT**
.. image:: /images/cwspnav1.png
2. Here, either create your student, or if the student is already in the dash, make a check by that student/s name.
3. Select the drop down action box located at the bottom left of the screen and select **Promote to Worker**

.. image:: /images/cwsp2.png

4. Once selected, the student/s will be made into a student worker- you can then view the new student worker in the student worker dash by clicking **CWSP**>**Edit Student Worker**

Creating Supervisor Logins
---------------------------

1. Under the CWSP section from the main SWoRD dash, select **work teams** and click on your desired work team.
2. Select an available login, or click the blue plus located to the right of the box.


.. image:: /images/cwspsuperlogin.png

**Things to keep in mind**
- You need access to create users.
- Supervisors must log in to the base site, not the admin site. 
- Do not mark these users (Company) as Faculty or Student users. Doing so will produce unexpected results.
- One work team may have an unlimited number of supervisor logins.
- Supervisor login is not related to the supervisor contact in anyway.

Student Pay Rates
---------------------
School staff are able to set a pay rate that an individual student and a company gets per hour. The two options shown below exist for instances in which a school takes an accounting fee cut of the paycheck. Individuals can set either pay rate they desire, neither is required.

.. image:: /images/studentpayrate1.png

**Note** Schools have the option of setting a default pay rate in SWoRD's configurations. This price will by default appear on time sheets and student worker pages, including being a default when new students are created. 

In instances where certain students get paid differently than others, you can edit the student/s by clicking on their individual student worker page as shown above, or mass editing the change from the student worker dashboard.


Supervisor View/Timecard Approval
---------------------------------
Once the student submits a timecard for approval, an email will automatically be sent to the student's primary supervisor asking for approval, as shown below:

.. image:: /images/supervisorview.png

The email will instruct the supervisor to click on the special link provided. Once selected, the supervisor will then be sent to the time sheet the student submitted that displays what the student did, time in, time out, etc.

.. image:: /images/supervisorview2.png

From here, the supervisor may write questions/comments in the provided text box, as well as provide an evaluation from a drop down box- these options may be customized to fit a school's need. When the supervisor approves the time card, work study staff will see it marked as approved in the time sheet dashboard.


Electronic Contracts
----------------------

SWoRD supports the ability to store and sign fully electronic work study contracts between the school and the student's work placement. Contracts can be filled out by the client from a web interface, or manually added to a company under the **Companies** selection from the CWSP header. 

**Note:** Contracts are linked to companies, not work teams.

1. For fully electronic contracts, start by editing or creating a template, and be make certain that it's named "Work Study Contract". If your school has purchased SWoRD support, feel free to email for assistance in this  regard, otherwise refer to the "Report Writing and Creating Templates" section above to do so indepedently. 

.. image:: /images/cwspaddtemplate.png

2. Next, you will need to generate special web links for **each** company you want to get a contract from. It is recommended that you try this first with a fake companay to see how it works.

3. To get to this link, enter <site url>/work_study/company_contract/<company id #> Where site url is replaced with the URL for your SWoRD installation. Company ID # can be downloaded with the export to XLS tool. Go to **companies**, check off the companies you want to get IDs for, click **Export to XLS** and make sure the ID column option is checked.

A finished url might look something like: sis.YOURSCHOOL.org/work_study/company_contract/123

You may send this link to your client and wait for the results to come in. Because SWoRD stores contracts, you may review it once it has been submitted under Work_study > Company Contracts.


Message to Supervisors
------------------------
SWoRD allows school officials to send out messages/reminders for all supervisors to see when they log in to approve a student's time card. The steps are as follows, with an attached picture depicting the steps and outcome:

1. Under **Company Data**, select ADD under the *Message to Supervisors* subheading.	
2. Type out your desired message to display to all supervisors.
3. Select a Start and End date to indicate how long the message will be visible.
4. Click Save.

.. image:: /images/msgtosuper.png

After the previous steps above have been completed, SWoRD will then display your message to supervisors on their dashboard page, as shown below:

.. image:: /images/msgtosuper2.png


===================
Volunteer Tracking
===================

Some schools require students to complete a certain number of volunteer hours every school year. Accordingly, SWoRD allows school staff to keep track of a student's volunteer hours, sites, and site supervisors. Tracking volunteers works similar to other modules in terms of adding and storing data.


Adding a Volunteer
-------------------
Locate the **Volunteer_track** module of SWoRD from your main dashboard screen. Once found, select **add** by the **volunteers** option. The following page will be displayed:

.. image:: /images/volunteeradd.png

Under **student** begin typing in the name of a student you will be adding as a volunteer. A list of students will then show in a drop down box. Once your selection has been made, the remaining fields are optional- hours required, notes, sites. Select **Save**.

Volunteers will be stored under the **Volunteers** heading along with their progress in number of volunteer hours completed.

.. image:: /images/volunteersstored.png



Add a Site for Volunteers
----------------------------
**Sites** refer to the physical location of where students will be volunteering. In the volunteer track module, the **volunteer sites** option is for school staff to create a new volunteer session for a student without the student submitting.

From the **Volunteer Tracking** header select +Add by the Sites option.

.. image:: /images/volunteeraddsite.png

Next, you'll see the image below directing you to fill out basic site information. Save your changes.

.. image:: /images/volunteeraddsite2.png


Assign a Site Supervisor
--------------------------
At the familiar **Volunteer Tracking** module, select +Add next the **Site supervisors** option.

.. image:: /images/volunteeraddsuper.png

From this screen, add your information in about the supervisor. Note: only the NAME field is required, although ideally you could set the **site** of where this person is in charge of at this screen as well.


Add Volunteer Site
---------------------
Selct +Add by the **Add Volunter Site** on the Volunteer Tracking module. Clicking add will lead to the following screen:

.. image:: /images/volunteeraddvolsite.png

Here, you may enter the appropiate information in to register hours for a particular student. 

.. image:: /images/volunteerhours.png

Once the hours have been registered, you will see this reflected in the volunteer dash.

.. image:: /images/volunteerslistwithhours.png


=======================
Custom Report Builder
=======================

Packaged with every instance of SWoRD is the custom report builder tool. This tool allows users with permission to easily create custom reports utilizing a drag and drop method. This section will cover how to utilize this tool.


Report Builder Dashboard
--------------------------
Access the admin report builder site (sampleurl/admin/report_builder) and click **reports**. The following report builder dashboard screen appears:

.. image:: /images/reportbuilderdash.png

This dashboard will allow the user to view any reports that have previously been created. Additionally, users will have the option of utilizing the available filter to quickly access, sort, and view previous reports by status, date, and root model.

**Starred Reports** are utilized to mark important reports, or reports that will be frequently generated. Users may quickly sort the dash to view only starred reports by selecting the **View Starred Reports** button located towards the top of the dashboard.

Creating a Report
--------------------
From the report builder main screen described above, select **Add Report** located at the top right-hand corner of the dash. The *Add Report* screen displays- **name** and **root model** (students, applicants, workers, etc.) are required fields.

.. image:: /images/addreportscreen.png

It may also be helpful to include an extended description as shown above to provide other users with a more clear direction of how the report is used. Once the information has been entered, select **Save** Your newly created report will now show as the most recent report in the dash, where you can then edit accordingly: 

.. image:: /images/newreportindash.png

Editing a Report
------------------
All created reports have the option of being edited. Using the newly created report from above, to begin editing, select the pencil icon located under the **Edit** column by the respective report, in this instance: Basic Student-Worker Information.

.. image:: /images/editreportscreen.png

With the **Report Display Fields** tab selected at the top, click and drag the fields from the list of available options located at the bottom-left side of the screen into the empty area located directly to the right while the appropiate tab is still selected. **Save** your selection.

*Note:* The **Expand Related Fields** field located in the box above the current fields list allows users to access expanded fields/information. Selecting one option will generate the expanded fields in the box below where you can then drag and drop into the space available accordingly.

After dragging your specified fields and saving, users then have the option to preview the report by selecting the **Preview Report** tab. This will generate a preview, where users can then export into an Excel/Libre-Calc document, as shown below:

.. image:: /images/previewreport.png

Using the Report Filters Tab
------------------------------
The **Report Filters** option is designed to give users the ability to further refine their data. Refining information functions similiar to editing your report, simply select the **Report Filters** tab and use the available fields list on the bottom left to drag and drop into the empty area. 

Using the example above, consider the use case of a user wanting to pull the student-worker data from before, but only for males working on Mondays.

1. Drag and drop **Working day** and **sex** into the open area as shown below.
2. Under the **value** header, select Monday, and Male accordingly.
3. Click **Save** then enter preview tab to view and download into Excel.

.. image:: /images/reportfilterstab.png







