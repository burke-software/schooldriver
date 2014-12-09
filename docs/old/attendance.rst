.. _attendance:

Attendance
====================
Django-SIS has a built-in attendance module that allows teachers to record daily attendance. Homerooms must already be in place, which are simply courses that are designated as such. 


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

Mass Edit Attendance
---------------------
Django-SIS allows users to edit multiple records at once, using the mass edit tool as detailed and shown:

1. Select Attendance > Edit
2. Select students for edit
3. Select "Mass Edit" from the actions menu located at the bottom left of your screen.

.. image:: /images/atndmassedit1.png

4. The next screen will allow fields to be changed for all checked off records. Leaving a field blank will not change the record. 

.. image:: /images/atndmassedit2.png

5. Select the correct field for mass update ("status" in this case)
6. Save
