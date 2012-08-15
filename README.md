#Django-sis 
This is an open source school information system built with Django. It relies heavily on the django admin interface for backend usage (registrar, etc). Below you will find a list of apps included in the software with a brief description of each.

# Apps

##School Information (sis)
This tracks the students’ information and their parent/guardian/contact information. This module also records cohorts (groupings of students for easier class enrollment), basic faculty information, and school year information. This is the central module for django-sis and is required for use of any other module. All other modules are optional.

##Admissions
This tracks potential students and their registration process. It allows various admission levels to be added, as well as steps that need to be completed before moving onto the next level. It also tracks any open houses a student has attended and how the student heard about the school.

![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/funnel.png)

##Alumni 
This tracks what college a student has enrolled in after graduating, and any alumni actions (such as reunions). Information can be imported from National Student Clearinghouse (http://www.studentclearinghouse.org/).

##Attendance 
This tracks students’ daily attendances. It allows for homeroom teachers to take attendance each day.

![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/attendance.png)

##Discipline
This tracks students’ discipline information, which includes infractions and actions to be taken, as well as the teacher who reported the infraction (if necessary)

![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/discipline.png)

##Schedule, Courses, and Grades
This module tracks courses, enrollments, marking periods, class periods, marking period grades, student awards, and standardized tests information and results (ex: SAT, ACT, etc). We currently do not support a full gradebook and Engrade should be used for seamless integration.

##Volunteer Tracking
This module tracks any volunteer work a student is required to do. Site information and site supervisor information are tracked. A student can volunteer at multiple sites.
Counseling: This tracks students’ counseling meetings and referrals. It allows teachers to submit online referral forms that notify the counselor. It also tracks follow up actions after the meeting.

##Work Study 
This module involves many different facets. Students from the School Information module can be converted to Student Workers so that more specialized information can be tracked in the Work Study module. 
  Work attendance can be tracked. 
  Basic company information is stored
  Students  are separated into “workteams” – groups of students that split a full time equivalent job. 
  Companies can have many workteams. 
  Students can enter timesheets for supervisors to approve and make notes on and evaluate the student. 
  Company Visits can also be tracked
  Department of Labor forms are able to be inputted electronically




