.. _djangogradebook:

Django-SIS Gradebook
=======================

Django-SIS comes packaged with a gradebook for teachers to utilize to store and track grades. This section will discuss and review how to use and configure the gradebook for your needs.


Accessing the Gradebook
------------------------

To access your gradebook to submit grades, do the following:

1. Log in to Django-SIS
2. Select **Submit Grades** from the *Student* drop down at the top menu.

.. image:: /images/gradebook1.png

3. Django-SIS will show you a list of your courses. Click on **Gradebook** by the appropriate course.

.. image:: /images/gradebook2.png

4. The gradebook for the selected course will then open up.

Creating Assignments 
------------------------------------------

After you've accessed your gradebook, and you're ready to create assignments:

1. Select **Create New Assignment** from the gradebook.

.. image:: /images/gradebook3.png

2. Once selected, a dialog box will pop up asking you to enter information about your assignment. Enter your information and submit. 

**Note:** You'll want to ensure that you enter a **category** for weighting purposes. *Standard* and *Assignment Type* here are optional and used for benchmark grading purposes, and might not apply to you (the options will be blank if not applicable for you).

See the image below:

.. image:: /images/gradebook4.png

**Note:** Django-SIS will calculate grades based off the number you enter for **points possible**. For example, if your assignment is one where 10 points is the max, and a student gets a 7, that will accordingly effect his overall average as if it were a 70. 

3. Your newly created assignment will now be listed as a column header. Hovering your mouse over it shows the details of it. See image.

.. image:: /images/gradebook5.png

Entering Grades
-----------------------------

Entering grades for assignments is a straightforward process and can be done in two ways:

1.) **Manually enter grades for each student**

-This process involves clicking on the appropriate cell by the student, and typing in a grade. After you type in a grade, press Enter or click on the next cell. 

The example below shows an instance of giving student *Jane Doe* a grade of 7.5 for the **Greet your neighbor** assignment that is graded out of 10. 

.. image:: /images/gradebook6.png

2.) **Using the fill-all feature**

-This feature can be used on assignments, and will fill all student grades with whatever you enter. Accordingly, it's best used when the majority of students received the same grades where you then change the few unique grades.

How to: click the little blue symbol by the assignment. 

.. image:: /images/gradebook7.png 

A dialog box will pop up with the assignment name asking you what grade all students should receive:

.. image:: /images/gradebook8.png

Enter a value and **submit**.

Other Notes for Teachers
-------------------------

-The title of your course gradebook that you see at the top is whatever your registrar has entered as the **shortname** for the course. This can be changed. Email your registrar who created the course and ask for a change if you need one.

In this example, the full title of the course is "My Test Course", however, on the gradebook I see "MTC" Gradebook, as the registrar had "MTC" as the **shortname**. 

.. image:: /images/gradebook9.png

.. image:: /images/gradebook10.png

-**Course averages** for students will calculate automatically after you enter a grade. *Filtered Average* won't update until the page is refreshed or the filter is changed.

-**Class average** will also calculate automatically.

-Always enter a category for assignments so Django-SIS knows how to calculate averages.

-**Course average** column is what students will see as their grade for the course on report cards.

Grade Calculation Rules
-------------------------

**Note** This section is mostly intended for registrars, as it involves special permissions to access and edit. Calculation rules must be set prior to utilizing the django-sis gradebook, so the gradebook can know how to calculate averages correctly.

To access grade calculation rules:

1.) Click on *View Site Admin* at the top right of django-sis.

2.) Under the *Courses and Grades* heading, select *Calculation rules*

3.) Click add rule if a calculation rule does not exist.


**Note:** Once you set up a calculation rule, it will automatically apply to every subsequent year, unless you create a new, more recent rule. They do not need to be set every year, unless the calculation rules at your school change.

There are three setups required at the calculation rule page: first year effective, points possible, and decimal places. 

**First year effective** - the school year to first apply the grade rules to.

**Points possible** - number field. Maximum amount of points for each grade book entry. 100 is typical.

**Decimal places** - number field. How many decimal places should be included for each gradebook entry.


The section below the above requirements is titled, *Categories included in each course average*. This is where the registrar sets up how categories will be weighted. There are three columns in this section: category, weight, and apply to departments.

**Category** - categories are types of assignments teachers may enter grades for. Ex. Quizzes, Major Assignments, Character Counts, Tests. Teachers are **required** to enter a category type when they are entering a new assignment in the gradebook to grade.

**Weight** - how to weigh each category. ex. if you have 4 categories, you can break them up equally by assignining a weight of 0.25 for each.

**Apply to departments** - which apartments these categories and weights effect.


Be sure to save after assigning categories, weights and departments.


How Course Grades are Calculated
---------------------------------

This section is intended for any staff interested in how django-sis calculates grades.

Final grades may be calculated in two ways. First, the software will look to see if any final grades have been overrided. In other words, if a registrar manually alters the final grade on a gradebook, that new grade will remain.

If there are no overrides, the final grade for a course will be the weighted average of the number grades accordingly.


If a particular assignment entry is a Pass or Fail (indicated by a P or F, respectively) then the gradebook will initiate a special letter grade calculation where P = 100%, and F = 0%. Since the gradebook will take averages, 2 P's and 1 F will result in an average of 66.66%. Keep in mind the teacher will always just see a P or F.

Some calculations may have dates attached for historical purposes or different marking period weights throughout the year. 
