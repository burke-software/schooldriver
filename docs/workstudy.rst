.. _workstudy:

Work Study
=================
The Django-SIS work study module allows users to keep track of student worker information, including: detailed company information, work assignments, work attendance, directions, work teams, performance reviews, time sheets and more.

Electronic Time Card System
-----------------------------
At the heart of Django-SIS's work-study module is the electronic time card system. The electronic time card system allows the school to keep track of a student's working day, what that student did at work, and how their work supervisor felt the student did on a particular day. Additionally, all time cards created by students will be stored neatly into Django-SIS where work-study staff can then filter or create reports accordingly. The basic steps are outlined in the image below:

.. image:: /images/timecardprocess.jpg

Django-SIS then stores all timecards in the main timecard dash. Users with access to these stored time sheets are able to view each time sheet’s information including date, hours, student accomplishments, and supervisor comments.


.. image:: /images/timesheetdash.png

Adding a Student Worker
--------------------------
To create a student worker, staff members are only required to add a student. All students in the software will immediately be made into student workers.

1. Access the student dash by selecting **Student** at the navigation bar, then **EDIT STUDENTS**

.. image:: /images/cwspnav1.png

2. At the list of students screen, select **Add Student** at the top right of your screen.
3. The only **required** information when adding a student is the username. Everything else is optional.
4. Select **Save** at the bottom right of the screen.

You may now access the list of student workers by clicking CWSP at the top menu bar, then clicking on **student workers** under the **EDIT WORK STUDY** dashlet. Your newly created student/worker will now be available to assign work placements, supervisors, etc.


Creating Supervisor Logins
---------------------------

1. Under the CWSP section from the main Django-SIS dash, select **work teams** below the **edit work study** dashlet and click on your desired work team.
2. Select an available login, or click the blue plus located to the right of the box.


.. image:: /images/cwspsuperlogin.png

**Things to keep in mind**

- You need access to create users.
- Supervisors must log in to the base site, not the admin site. 
- Do not mark these users (Company) as Faculty or Student users. Doing so will produce unexpected results.
- One work team may have an unlimited number of supervisor logins.
- Supervisor login is not related to the supervisor contact in anyway.

Creating Contact Supervisors
-----------------------------

Contact supervisors are individuals at companies that supervise a school's student worker. Accordingly, these contact supervisors are those people who will be receiving emails to evaluate/appraise a student worker's time card that has been submitted to them. To set them up, follow the directions below:

1. Under the **Edit Work Study** dashlet from the CWSP Django-SIS dash, select Add+ by **Contact Supervisors**
2. Fill out the available data fields.
3. Save

Once the contact has been created, that contact may be assigned to any number of work teams. To assign your newly created supervisor to a work team, click on **Work teams** under *Company Data* and scroll down to the **Contacts** box. Select a contact from *available* and switch them to *chosen* as shown below:

.. image:: /images/contactsupervisor.png 

**Don't forget to click SAVE after assigning a Contact**



Work Teams
------------------

Work teams are a single student, or group of students that are assigned jobs at a company. Work teams are especially helpful for when a school has multiple students working at the same company, but have different types of jobs at that company. For example,

Student A and Student B both work at Sample Company, but in different departments.

Work teams allow schools to create unique work teams that are still associated with the same company:

Student A - Sample Company Front Office
Student B - Sample Company Marketing Dept.

**Creating Work Teams**

1. Select Add+ by **Work Teams** located under the *Edit Work Study* dashlet.
2. Fill out the information available. A team name is *required*. 
3. Save

In the example image below, a work team, *Wells Fargo Marketing Dept* is created and is associated with the company, *Wells Fargo*

.. image:: /images/workteam1.png 


Assigning Work Placements
--------------------------

Once all the work teams have been created, you can now assign student/s to a work team. To do so, follow the directions below:

**For a single student**

1. Click on student worker's name
2. Assign the student a placement from the dropdown box. *Note*: placements refer to workteams (see above)

.. image:: /images/assignworkplacement1.png 

3. Save

Once saved, you will see the changes reflected immediately in the student worker dash:

.. image:: /images/assignworkplacement2.png 

**Multiple Students**

Using the Mass Edit function, work study staff can assign multiple students to the same work team quickly, instead of assigning by individual student. To do so:

1. Go to the **Student Worker** dashboard, and select your students to group assign placements.
2. Once seleted, click **Mass Edit** from the black toolbar at the bottom.

.. image:: /images/assignworkplacement3.png

3. At the mass edit screen, check the box by placement and assign a placement.

.. image:: /images/assignworkplacement4.png

4. Save

You will now see the changes reflected on the dashboard:

.. image:: /images/assignworkplacement5.png

Student Pay Rates
---------------------
School staff are able to set a pay rate that an individual student and a company gets per hour. The two options shown below exist for instances in which a school takes an accounting fee cut of the paycheck. Individuals can set either pay rate they desire, neither is required.

.. image:: /images/studentpayrate1.png

**Note** Schools have the option of setting a default pay rate in Django-SIS's configurations. This price will by default appear on time sheets and student worker pages, including being a default when new students are created. 

In instances where certain students get paid differently than others, you can edit the student/s by clicking on their individual student worker page as shown above, or mass editing the change from the student worker dashboard.


Supervisor View/Timecard Approval
---------------------------------
Once the student submits a timecard for approval, an email will automatically be sent to the student's primary supervisor asking for approval, as shown below:

.. image:: /images/supervisorview.png

The email will instruct the supervisor to click on the special link provided. Once selected, the supervisor will then be sent to the time sheet the student submitted that displays what the student did, time in, time out, etc.

.. image:: /images/supervisorview2.png

From here, the supervisor may write questions/comments in the provided text box, as well as provide an evaluation from a drop down box- these options may be customized to fit a school's need. When the supervisor approves the time card, work study staff will see it marked as approved in the time sheet dashboard.

Work Study Attendance
------------------------

Work Study staff members are able to track their own attendance. By selecting "Take today's attendance" button from their CWSP Attendance dashlet.

 .. image:: /images/wsatnd1.png

 Django-SIS will then display a list of students whose working day is that particular day, as shown:

 .. image:: /images/wsatndlist.png

 Once submitted, Django-SIS will then display both Present students and Absent students in the dashboard, in addition to Tardy and Absent/Half Day as they are marked by homeroom teachers. This allows work study staff to determine whether or not a student should submit a time sheet. 

 .. image:: /images/wsatnd2.png


Electronic Contracts
----------------------

Django-SIS supports the ability to store and sign fully electronic work study contracts between the school and the student's work placement. Contracts can be filled out by the client from a web interface, or manually added to a company under the **Companies** selection from the CWSP header. 

**Note:** Contracts are linked to *companies*, not work teams.

1. For fully electronic contracts, start by editing or creating a template, and be make certain that it's named "Work Study Contract". If your school has purchased Django-SIS support, feel free to email for assistance in this regard, otherwise refer to the "Report Writing and Creating Templates" section above to do so indepedently. 

.. image:: /images/cwspaddtemplate.png

2. Next, you will need to generate special web links for **each** company you want to get a contract from. It is recommended that you try this first with a fake companay to see how it works.

3. To get to this link, enter <site url>/work_study/company_contract/<company id #> Where site url is replaced with the URL for your Django-SIS installation. Company ID # can be downloaded with the export to XLS tool. Go to **companies**, check off the companies you want to get IDs for, click **Export to XLS** and make sure the ID column option is checked.

A finished url might look something like: sis.YOURSCHOOL.org/work_study/company_contract/123

You may send this link to your client and wait for the results to come in. Because Django-SIS stores contracts, you may review it once it has been submitted under Work_study > Company Contracts.


Message to Supervisors
------------------------
Django-SIS allows school officials to send out messages/reminders for all supervisors to see when they log in to approve a student's time card. The steps are as follows, with an attached picture depicting the steps and outcome:

1. Under **Edit Work Study** dashlet, select ADD under the *Message to Supervisors* subheading.    
2. Type out your desired message to display to all supervisors.
3. Select a Start and End date to indicate how long the message will be visible.
4. Click Save.

.. image:: /images/msgtosuper.png

After the previous steps above have been completed, Django-SIS will then display your message to supervisors on their dashboard page, as shown below:

.. image:: /images/msgtosuper2.png

CWSP Reports
--------------

Similar to other modules, the Work Study module in Django-SIS comes packaged with a number of pre-built work study reports. In addition to the pre made reports, there is a section available for template based reports which will generate reports that a user has created. A description of the three major types of reports, along with examples will be shown below:

**Pre-made Reports**

The pre-made reports are one click reports that cover: FTE, MISC, Atendance dropoff, Attendance Pickup.

.. image:: /images/cwspreportspremade.png

*FTE reports:* (Full-time equivalent): by industry, day, and paying status will generate an overview and a per student look covering the aforementioned filters.

**MISC** 

*Company History:* Will generate an Excel document detailing all student placements at a company by date. 

*Master contact list:* Produces an Excel document showing all student contacts- their work contacts number/email and each parent email/phone number.

*Contracts report:* Excel document showing each company, whether or not there is a contract, and when the date for the last contract was recorded.

*Attendance Dropoff and Pickup:* Shows each student worker attendance that is working on the designated day you click, along with transportation information (subway line, stop location) and associated company.

**Date based reports**

These reports require the user to set up a date range. Once the date range is set, the user may click on a report in which Django-SIS will tailor to the dates accordingly.

.. image:: /images/cwspdatebasedreports.png

*Attendance and missed day report:* Multi tabbed Excel document that displays students who missed their work day, and if/when that work day will be made up along with comments and totals. Additionally, a separate tab will display all student worker time sheets that were submitted during the date range.

*Billing and timesheet report:* Produces a billing report for the date range, including hours worked, and amount to be billed (multiplies hours worked by school pay rate to arrive at a total) to each company. This report breaks the billing and timesheet reports down by student.

*Students who submitted timesheets:* lists name of all students, and how many time sheets they submitted (including dates) during the date range set.

*Time Sheet Data:* Detailed look at all submitted time sheets during the specified date range.

*DOL Report:* Displays a school work study employee's visits to client companies for the date range.

**Template Based Reports**

These reports allow users to generate reports that they have created themselves, although Django-SIS does come packaged with some already made generic templates, including a travel maps/directions to help work study students get to their work site, as shown below:

.. image:: /images/cwsptemplatebasedreport.png
