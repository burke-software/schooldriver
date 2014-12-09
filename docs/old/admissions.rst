.. _admissions:

Admissions
=====================

The admissions module allows schools to keep track of applicants, and their status in the application process. Each step in the application process can be customized to fit a school's unique need. Users can designate steps that need to be completed before moving onto the next level. Additionally, Django-SIS may track any open houses a student has attended and how the student heard about the school. 

.. image:: /images/applicantdashboard.png

The image above details the dashboard that an admissions counselor or designated user sees when the admissions module is selected. Most modules include a dashboard to provide users a general overview of information that is able to be filtered. 


Adding an Applicant
--------------------
To add an applicant: 

1. Select **Applicants** under the Admissions module.
2. Enter information about the applicant accordingly. First and Last Name fields are required.
3. Click **Save**.

Django-SIS will then return you to the applicant's dashboard where you will see your newly-created applicant at the top.



Admissions Levels
------------------
Django-SIS allows schools to control admissions levels/steps that are unique to their process. Each step is customizable as follows:

1. Select **Admissions Levels** under the Admissions module.
2. You will see the screen shown below.

.. image:: /images/admissionslevel1.png

3. From this screen you can add an admissions level, selecting the **Add Amissions Level** button or edit an existing one by selecting *edit* located next the level you are altering. From the edit screen or add screen, make the necessary changes/additions and then select save.

The section under the header, **Items needed to be completed to attain this level in the process**, refers to creating a checklist of various tasks the applicant needs to complete prior to reaching a new step. For example, the image below details a checklist containing the two required tasks 'Open House' and 'Request more information' which must be completed before the applicant reaches the level of Inquiry. 

.. image:: /images/admissionslevel2.png

Users may designate levels required in order to advance. For example, schools may require an applicant pay an initial deposit prior to registration. To make a step required, simply check the box found under the **Required** column and save.


Filtering Applicants
---------------------
To maximize organization, efficiency, and promote the ease of collecting various admissions data for report preparation, Django-SIS contains several filters and functions accessible through the main applicant page. Each column header in the image below will sort accordingly. For example, clicking on Last Name will filter by last name, application decision by decision, etc. 

.. image:: /images/applicantsalpha.png
Alternatively, users may choose from the available filters located directly to the right of the applicant list. The drop down list allows users to select and combine the following filters: school year, level, checklist, ready for export, present school, ethnicity, heard about us, and year. The filter tool will do so in real time, no need to select and save.


Exporting Applicants
---------------------
Django-SIS allows for easy export into an Excel document for sharing or distribution. After applying filters to applicants, follow the steps below to export into an Excel file.

1. Select each applicant you would like to export or select all by selecting the top left checkbox.
2. Click the drop down menu located on the black toolbar at the bottom of the page.
3. Select **Export to XLS**. A box opens up with options on what to export.
4. Choose Select All to export all information entered for each applicant or check specific boxes.
5. Scroll down and select **Submit**.
6. Django-SIS will then open an Excel document.


Admission Reports
--------------------
Some basic Admission Reports are available built in to Django-SIS that allows users to quickly process statistics based on a school year's applicants. 

1. Under the **Admissions** tab in the navigation bar, select **Reports**

.. image:: /images/admreports1.png

2. Select a year and click **Process Statistics**.
3. Django-SIS will generate an Excel document detailing some basic admission statistics such as number of applicants by grade or number of applicants on a particular level in the process.  

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
