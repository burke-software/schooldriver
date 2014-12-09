.. _discipline:

Discipline
===================

The discipline module tracks a student’s discipline information including infractions, actions to be taken, and the teacher who reported the infraction. Similar to the other modules in Django-SIS, discipline reports can be generated and exported into an Excel document. 

View Discipline
-----------------
For fast lookup of a particular student's discipline record:

1. Select **Discipline** from the navigation menu, then **View**. 
2. Begin typing in the name of the student in the text box, and Django-SIS will present you with a list of available students as shown below:

.. image:: /images/viewdiscipline.png

3. Once a particular student has been selected, Django-SIS will present all discipline information that has been input for the student:

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

*Schools beginning to use Django-SIS should add all discipline actions that the school currently utilizes.* 

.. image:: /images/disciplineactions.png
