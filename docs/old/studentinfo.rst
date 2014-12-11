.. _studentinfo:

Student Information
====================
The SIS is the central module of Django-SIS which contains profiles, attendance, discipline, work study, and other details pertaining to the student. For information on admissions, adding students, attendance, and discipline, please follow the pertinent headings. 

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
Year classifications are the various grades Django-SIS supports and their associated names. The defaults in Django-SIS are:

- Freshman: 9
- Sophomore: 10
- Junior: 11
- Senior: 12

Student Phone Numbers
-----------------------

In Django-SIS, you will see areas for Student phone numbers and for Student Contact phone numbers.
To get proper information out of the system, you need to enter the numbers in the correct areas.

**Student phone numbers-** are for numbers to contact the student, for example a student's cell phone.  If you use the home number in this spot, you should also put it into the contact area for the parent.

**Student Contact phone numbers**- cell, home, and work phone numbers for parents or other emergency contact personnel.

Student Contacts
--------------------
The student contacts facet of django-sis refers to the parent or guardians associated with a student.

**Accessing the contacts**

There are two ways to add contacts. The first and easiest method is located on the student page in its own section titled, "Student Contact" respectively. 

To add contacts, simply select a student from the Student > Edit page, or create a new student and scroll down to the *Student Contact* section and select **add**. Fill out the information in the dialog box and save.

The other method of accessing contacts works as follows:

1. At the top right of your screen, select **View Site Admin**
2. Select **Student Contacts** from the *School Information* heading
3. Click **Add student Contact** at the top right, fill out available information, and save.


**What you can enter about each contact:** first name, last name, middle name, relationship to student, email, primary contact (checkbox), emergency only (checkbox), address, phone numbers, and student.

Family Access Users
---------------------

Django-SIS allows for parents/guardians to log in and view grade information pertaining to their child. This section will show registrars or admins how to set up parent logins. 

1. Under the **School Information** tab, select Add+ by the choice, **Family Access Users**

.. image:: /images/famaccess1.png

2. Create a username and password for the parent.
3. Return to the **Students** page, and under **Family Access Users**, select the user/s you've created that are in the left box titled *Available family access users* and click the arrow so that the user names switch to the right box titled, *Chosen family access users.*

.. image:: /images/famaccess2.png

4. Save   


Cohorts
-----------------------
Cohorts are groupings of students within a school; the registrar may find this tool useful. For example, an "advanced class" cohort may be enrolled in particular classes, and homeroom placements may also be organized using cohorts.


Creating Courses
------------------

Creating courses in Django-SIS is a 3 step process:

1. Under the Courses and Grades tab, select +Add under **courses**

.. image:: /images/sisaddcourses.png

2. At the add course screen, enter any information that's appropiate- teacher, description, graded, etc. Keep in mind that the only **required** options to fill out are Fullname and Shortname.

3. Save

Enrolling Students
--------------------

1. Under the Courses and Grades tab, select **courses**.
2. You'll be taken to a screen of all available courses, as shown below:

.. image:: /images/siscourseview.png

3. Select the course you will be enrolling students in.
4. Once selected, you will be taken to the change course screen. Click the **Enroll Students** button located towards the top right of the screen. 
5. The screen below appears- move student/s from the available students box on the left, into the *chosen students* box on the right. You may filter the available students by grade level, located directly above the *available students* box.

.. image:: /images/sisenrollstudents.png

6. Save 

Submitting Grades
-------------------
Teachers may submit grades using three methods: manually, import via spreadsheet, or using Engrade.

**IMPORTANT:** Django-SIS only stores final grades.

**Manual Method**

The manual method of entering final grades works as follows:

1. Under the Courses and Grades tab > Courses, click on the appropiate course.
2. Once selected, click **Grades** on the course page, located towards the top left.
3. You'll be taken to a screen as shown below. Click on the cell and type a grade, then save.
.. image:: /images/gradesmanualentry.png

**Spreadsheet Method**

NOTE: Only final grades are stored in Django-SIS. Assignments should be stored in a Spreadsheet based on a template your administrator created. 

Access the course page, similar to step 1 from above.

1. Under the Courses and Grades tab > Courses, click on the appropiate course.
2. Select **Gradesheet Template**. It will open up an Excel file already set up for grade input with usernames and students already available for you, per the template. Fill out your grades and note any comments.

.. image:: /images/gradesspreadsheet.png

3. Once the template is filled out. Select **Grades** from the course page.
4. *Ensure* that the marking period is correct and matching the **tab name** on the spreadsheet you filled out. Select **Upload**

.. image:: /images/gradesspreadsheet2.png

5. Django-SIS will then set the grades and comments in accordance with your spreadsheet. 

.. image:: /images/gradesspreadsheet3.png

- Final grades are calculated automatically, but may be overridden by privileged users.
- Mid marking period grades will never effect any calculation.

*Grade Comments/Comment Codes:*

- Comments may be entered via plain text or comment codes as designated by your school. If you wish to enter multiple comment codes per student, a comma separating each code is necessary (i.e.14, 3).
- Blank comments or comment codes will be ignored.
- If a comment or code already exists and you want to delete it, select the code and replace it with "none".


*Tips:*

- Django-SIS stores only two decimals, although calculations may be done with more.
- You may enter approved Letter grades if desired such as P and F. These will not effect calculations.
- You may only be allowed to change specific marking period grades determined by your administrator. If you've made a mistake you may need to contact an administrator or registrar. It is possible to grant you access to directly enter grades in Django-SIS. This may be useful for Pass/Fail grades.

**Engrade Method**

Django-SIS is able to sync with the online gradebook, Engrade so teachers my store all assignments there, then sync final grades there to appear in Django-SIS.

 1. Under the Grades menu item at the top, select **Submit Grades** 
 2. This will reveal your list of courses, along with the option to download a blank gradebook. Below these options is the button **Sync all grades from Engrade**. 

 **Keep in mind that all grades synched from Engrade will override any grades that have been entered into Django-SIS for that marking period.**

Standard Tests
-----------------------

Django-SIS allows users to create and enter information for various standard tests (ACT, SAT, PLAN, etc.).

**Creating a New Standard Test**

1. Under the *Standard Tests* tab, select +Add by the **Standard tests** option.

.. image:: /images/standardtests1.png

2. Enter a name of the test and select the appropiate boxes on how to calculate test results.
3. The **Standard Category** tab refers to the categories of a test (English, Math, Science, Writing, etc.)
4. Save

**Recording Standard Test Scores**

1. Under the *Standard Tests* tab, select +Add by the **Standard test results** option.
2. Enter a date, select the student, and select the appropiate test.
3. Under **Standard category grades** select the cateogry and type in the grades.

**Note** You add additional categories by selecting *Add another Standard Category Grade (Math, then Science, etc.)

.. image:: /images/standardtests2.png

4. Save


Omit Course GPA
-----------------

Django-SIS allows users to quickly omit a student's grades for a particular course.

1. Under the Courses and Grades tab, select +Add by the **omit course GPA** selection

.. image:: /images/sisomitcoursegpa.png

2. Select the appropiate student and corresponding course.
3. Save


Omit Year GPA
---------------

Similar to omitting course GPAs, Django-SIS allows users to omit an entire year of grades for a student so that particular year will not be calculated into GPAs and transcripts. The process is similar to omitting for a course, as shown above.

1. Under the Courses and Grades tab, select +Add by the **omit year GPA** selection

.. image:: /images/sisomityeargpa.png

2. Select the appropiate student and corresponding year.
3. Save
