.. _admininfo:

Administrator Information 
=========================================
**Libreoffice on the server**

Should be run as an upstart job like /etc/init/libreoffice.conf::

    start on runlevel 2

    exec /usr/lib/libreoffice/program/soffice.bin '-accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' -headless

    respawn
    respawn limit 10 120

Then start with "start libreoffice"

User Permissions
---------------------
Django-SIS allows administrators to control individual user permissions. To simplify this process, Django-SIS groups individual permissions into larger groups which the administrator can designate accordingly. Some of the groups are as follows:

**Teachers**: Users with this designation may create tests, view students, enter grades, and take attendance.

**Counseling**: record student meetings, refer students, and list follow-up actions

**Faculty**: view alumni, students, and mentoring information

**Work Study**: view work study attendance, fees, visits, companies, payment options, contact supervisors, time sheets, surveys, assign work teams and work team users.

**Registrar**: edit templates, view applicants, edit admissions, view/edit attendance, add custom fields, sync Endgrade courses, create schedules, reports, transcript notes, and school years.

**Volunteer**: add/change/delete volunteer hours, sites, supervisors, and student volunteers


It is possible to assign individual user permissions that are found in one group to an individual user that only has permissions from another group. For example, you can assign a teacher (who only has teacher permissions) the ability to view a student's counseling records or work study information. This allows school administrators to create unique users with flexible permissions. Further, administrators can create superusers who have permissions from all groups. 

Importing Data Into Sword
-------------------------------
Django-SIS supports the import of data into its database.

In order to make the import process as simple as possible for schools transitioning into Django-SIS or schools preparing for the new school year, Django-SIS allows data to be imported via Excel or LibreOffice documents.

Keep in mind that this section is for **importing** data, and not *updating* data. This section assumes that students, applicants, etc. do not yet exist in Django-SIS (i.e.: new incoming freshmen or new applicants).

If you want to use simple import to mass update information (i.e: assigning existing student workers work days and placements). Then please refer to the next chapter.

**Before you Import**

Prior to importing data, you will need an Excel spreadsheet with information pertinent to the model you are attempting to import. Set column headers accordingly. Django-SIS is able to import all information that is able to be entered manually in a field. 

Keep in mind, the list below would be on a per import basis, and would be on a single Excel workbook. You cannot for example, import students and applicants in different workbooks. Save a new Excel file for each; the fields below will be the column headers on your Excel workbook, and the root models for import would be what's in italics. Here's a reference list of some column headers you can use for importing the most common models:

*Students*

Unique ID, First Name ,Last Name, username, grad date, Student cell ph, middle name,  class of year, STUDENT PHONE, GENDER, BIRTH DATE, Social Security, Student E-Mail, Alert, Primary Cohort, Parent email, homeroom, preferred language, picture, password

NOTE: First name, Last Name, and username/unique ID are required for importing new students.

*Student Workers*

First Name, Last Name, middle name, Username, notes, ADP Number, alert, alt email, am route, applicant, birth date, city, class of year, cohort, course, date dismissed, working day, placement, email, parent email, student pay rate, sex, SSN

*Applicants*

First name, Last name, middle name, birth date, present school, heard about us, first contact, withdrawn note, total income, adjusted available income, application decsion, application decision by, SSN, Sex, Ethnicity, Religion, Place of Worship, Year, School year, HS grad yr, Elem grad yr, email, notes, country of birth, family preferred language, lives with

*Marking Period*

Name, shorname, Start Date, End date, grades due, School year, weight (integer. ex. 1), active (=TRUE, or =FALSE), show reports (=TRUE, or =FALSE).

NOTE: name, shortname, start-end date, school year and weight are required fields.

*Courses*

Fullname, shortname, Marking Period, description, teacher (their username), homeroom (=TRUE, or =FALSE), Graded (=TRUE, or =FALSE), credits (integer field, ex. 1.0), department, level (Freshman, Sophomore, Junior, Senior).

NOTE: only fullname and shortname are required.

*Location*

Name

NOTE: This generally refers to a classroom name or location. Ex. Room 343

*Period*

Name, Start time, End time

*Family preferred Language*

Name, iso code (optional)

*Class Year*

Year (number- ex. 2014), Full name (ex. Class of 2014)

*Faculty*

Importing faculty essentially creates a user and assigns them the "faculty" permission. Designating =TRUE to the 'teacher' field just adds the 'teacher' permissions.

Username, First name, Last Name, email address, number, ext, Teacher (=TRUE or =FALSE)

NOTE: only the username field is required.

*Company*

This is for schools utilizing the CWSP module.

Name

*Work Team*

For schools setting up CWSP.

Team name, job description, company description, login (username), paying (=TRUE or =FALSE), Address, City, State, Zip, Travel route, Directions to, Directions pickup

The only required field is team name.

*Volunteer Site Location*

Only for schools planning to use the Volunteer module.

Site name, Site address, Site city, Site state, Site zip


NOTE: Django-SIS will guess matches based off your column headers, so if you enter First Name or fname, or FiRSt NaME as a header on your Excel doc, Django-SIS will determine which field that refers to.


**How To Import Data**

Importing data *requires* the appropiate permissions for the user. The method is described below:

1. Select Admin > School import from the navigation menu.
2. Enter a name for the import (can be anything).
3. Select browse to locate your Excel document
4. Under Import type, select from Create New Records, Create and Update Records, and Only Update Records. 
5. Select a Model. This refers to where you are importing the data. Select students for students, applicants for applicants, etc.

.. image:: /images/importcap1.png

6. Click Submit.
7. The next page will give users a preview of what their import will look like. Django-SIS tries to match the column headers in your document with an available field in Django-SIS. You can always edit the field (via drop down box) if Django-SIS displays an incorrect field.

.. image:: /images/importcap2.png

8. After you've matched all the fields to the sample data (i.e. SSN field actually displays a SSN in the sample data column), you can simulate the import or run it. Simulating the import won't actually import the data, but it will let you know in advance if there are any issues with what you're trying to import.

Updating data using Simple Import
------------------------------------

Some things to keep in mind prior to using the simple import for updating student data.

1. You will **always** need to have an update key. This lets Django-SIS reference what object is being updated. Typically, you will want to use a username, Django-SIS ID or unique ID. Getting IDs for objects is easy. Utilize the export to xls feature from your chosen page (student, student worker, applicant, etc.), and select ID, username or unique ID.
2. Data must already exist for that model. For example, you can't update information on a student that doesn't already exist. You **can** however utilize the "Create and Update" import type to do something like this, but this can't be done on the "Update Only" type. 
3. Make sure you select the correct model type.

**Example**

In this example, we will assume that we have a list of new freshmen who were just made into student workers. These student workers will now need their job placements and working days assigned. The picture below highlights the aforementioned:

.. image:: /images/simpleimportupdate1.png

1. Get the student worker usernames for update. These usernames will be used as the **update key**. This can be done by checking the box by each student and selecting *export to xls* from the action bar at the bottom of the student worker screen and check off *username*.
2. Using Excel, create a document with the column headers, **username**, **working day**, and **placement**.

.. image:: /images/simpleimportupdate2.png

3. Access the the simple import page. Admin > School Import
4. At this screen: name your import, select your Excel document, set the import type to **only update records**, and set the model to **student worker**. Click submit.
5. You will be taken to the match columns screen shown below:

.. image:: /images/simpleimportupdate3.png

NOTE: Notice in the image above I have selected username as the **update key**. As stated earlier, using either username, ID, or unique ID as the update key is easiest.

6. Click *next*. The match relations screen will ask how to reference a field- this will typically be by a name or ID. In the Excel document for import, we listed a team name for placement so in this example we will use team name instead of ID.

.. image:: /images/simpleimportupdate4.png

7. Click **Simulate import** to check for errors, then run.
8. Return to the student worker page, and your updated data will be displayed.

.. image:: /images/simpleimportupdate5.png

Configurations
---------------
Django-SIS contains a number of built-in configurations that are created with each new instance designed to make functions easier to edit or implement. 

For example, in configurations for email in the **How to obtain student email** function, users may designate three values designed to direct Django-SIS emails. 
**Append** appends the domain name after a student's username like jstudent@domainname.org. 
**User** takes the email address from the Auth->User record.
**Student** takes the email address marked from the *alt email* field of a student record page. 

Creating Users
--------------------

To manually add users, follow the directions below:

1. Under the **Administrators** panel, select Add+ by *Users*
2. Create a username and temporary password.
3. Next, you will need to edit the user. Select the newly created users from the users list.
4. Assign the user a name/last name- and ideally assign them a group, which will be discussed in the next chapter below.

.. image:: /images/adduser1.png


Overall, the groupings are self explanatory- if you're creating a registrar, assign them the **registrar** group, an admissions staff member would be assigned the **admissions** group, etc. 

Getting Started
----------------

**Server:** Django-SIS can be installed in any platform that can run Django. It should be noted, however, that all testing is done in Ubuntu Linux 10.04 with MySQL.

**Client:** Django-SIS is divided into two parts: the admin site and the student/company-facing site. The student/company-facing site is tested in Firefox, Chrome, Opera, and IE 6,7,8. The admin site is tested only in standards-compliant browsers such as Firefox, Opera, and Chrome. If using IE, you should install the Chrome Frame add-on.

**Editing Templates** requires Office software. Creating report templates require LibreOffice and *must* be saved in ODT format. Keep in mind that end-users may select their preferred office format preference, so ODT is *not* required to just view a report.

Using the ISO-supported Open Document format is recommended for best inter-operability, however doc and xls binary formats are highly supported. In rare cases, formatting may be slightly different in these formats. Office Open XML, while supported, is *not* recommended. 

Log Entries
--------------
Log entries record all actions completed during a Django-SIS's instance. This allows administrators and superusers to locate any changes made at specific dates or times. Admins will see a dashboard similar to what is shown below:

.. image:: /images/logentries.png

**User** refers to which user made a change.

**Action time** details the date and time when the change was made.

**Content type** is the model on which the change was made, e.g. applicant, student, etc.

**Object repr** assigns a specific name to the content type. For example, if applicant was the content type, then object repr will list an exact name like Joe Student.

**Is Addition, Is Deletion, Is Change**: True/False indicator which shows what type of action was completed.

Similar to other dashboards in Django-SIS, users may sort by clicking column headers and using the filter tool.

Templates
------------
All Django-SIS instances come packaged with a set of general templates. These templates allow users to generate a number of varied reports, including:Tardy Letters, Daily Attendance, Progress Reports, Transcripts, Travel Maps, Test Results, Discipline Report

A list of all available templates, free to download is found `here
<https://sites.google.com/a/cristoreyny.org/sword-wiki/preparing-for-a-new-school-year/templates>`_.

Django-SIS further allows users to create and edit their own templates to be used accordingly and will be discussed in the next section, Report Writing.

Report Writing and Creating Templates
---------------------------------------
**Note** Before you proceed, please be aware that in most cases it's best to simply edit existing templates found in your templates location, rather than creating entirely new templates as this section will discuss. 

Django-SIS provides the means for end users to create and utilize their own customized reports/templates. All reports are made using the `Appy Framework
<http://appyframework.org/pod.html>`_.

The basic process works like this: user creates report template in a word processor >>> the template gets uploaded into Django-SIS >>> Download/use finished report.

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

*Note:* You can see a list of available fields to choose from by typing this into your Django-SIS instance's URL. SAMPLESCHOOLURL/admin/doc/models. Some fields are calculated, for example he_she is based off of the sex of a student. Any type: list field cannot be used directly, but must be placed in a loop.

**Logic in Templates** You may use any Python logic in a template. For example in the above screenshot there is a note "do section for student in students". This logic can technically be placed in a field, however it's easier to read in a note. To create a note click Insert > Comment. In the example a section is being created for each student in the field "students". students is a list of students as defined in "School Reports" in Django-SIS. To create a section click Insert, Section. In the example the section includes a page break. Django-SIS will create a section (page break included) for each student in your list of students. This makes for similar results of a mail merge. You may also "do row" or "do cell" to create tables.

You may even include Django specific code, for example students.filter(fname="Joe") would result in a list of students with the first name of "Joe". For more see`Django's retrieving objects
<https://docs.djangoproject.com/en/dev/topics/db/queries/#retrieving-objects>`_. This may get complex fast, therefore Django-SIS offers some basic sorting and filtering options for you. See School Reports with Django-SIS. Essentially School Reports will give you the variable students, with your desired filters. If you selected only one student, you will instead have a "student" variable. From here you usually want some type of logic, such as do section for student in students. 

**Spreadsheet Reports** work differently. You can add additional fields to any student related spreadsheet. Select User Preferences and add additional fields here. These additional fields are defined by an administrator and follow the typical . notation (placement.address gets the address of the placement). The gradebook spreadsheet is a special case and a template can be used here. See the included template called "grade spreadsheet".

**Database Field Names** Click on Documentation, then Models to view various Database models. You can chain them by placing . to any related fields. For example student.placement.address would yield the address of the placement of that student.

Exporting Django-SIS data to Excel
-------------------------------
Django-SIS allows users to export into Excel any and all data that users have input into their respective Django-SIS instance. The process of exporting information is very simple, and detailed below:

    1. Click on any model you want to edit from your Django-SIS home dash- ex. students, applicants, student workers, discipline, etc.
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
