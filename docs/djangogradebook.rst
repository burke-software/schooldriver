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
