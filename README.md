Django-sis is a open source school information system build with Django. It relies heavily on the django admin interface for backend usage (registrar, etc).

# Apps
## sis
Core application - this is required to do anything.
## alumi
Keep track of graduated students. Import National Student Clearinghouse data. Add notes.

## admissions
Data about applicants. Can be imported into sis.
![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/funnel.png)
## attendance
Teachers can take attendance, adminstrative staff can view and edit.
![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/attendance.png)
## discipline
![Alt text](https://raw.github.com/burke-software/django-sis/master/screenshots/discipline.png)
## schedule
This app conains class schedules and is requires for other apps such as grades. 

##School Information (sis)
This tracks the students’ information and their parent/guardian/contact information. This module also records cohorts (groupings of students for easier class enrollment), basic faculty information, and school year information. This is the central module for SWoRD and is required for use of any other module. All other modules are optional.

##Schedule, Courses, and Grades
This module tracks courses, enrollments, marking periods, class periods, marking period grades, student awards, and standardized tests information and results (ex: SAT, ACT, etc). We currently do not support a full gradebook and Engrade should be used for seamless integration.

##Work Study 
This module involves many different facets. Students from the School Information module can be converted to Student Workers so that more specialized information can be tracked in the Work Study module. Work attendance can be tracked. Basic company information is stored, and students  are separated into “workteams” – groups of students that split a full time equivalent job. Companies can have many workteams. Students can enter timesheets for supervisors to approve and make notes on, as well as evaluate the student. Company Visits can also be tracked, and Department of Labor forms are able to be inputted electronically.

##Attendance 
This tracks students’ daily attendances. It allows for homeroom teachers to take attendance each day.
Discipline: This tracks students’ discipline information, which includes infractions and actions to be taken, as well as the teacher who reported the infraction (if necessary)

##Volunteer Tracking
This module tracks any volunteer work a student is required to do. Site information and site supervisor information are tracked. A student can volunteer at multiple sites.
Counseling: This tracks students’ counseling meetings and referrals. It allows teachers to submit online referral forms that notify the counselor. It also tracks follow up actions after the meeting.

##Admissions
This tracks potential students and their registration process. It allows various admission levels to be added, as well as steps that need to be completed before moving onto the next level. It also tracks any open houses a student has attended and how the student heard about the school.

##Alumni 
This tracks what college a student has enrolled in after graduating, and any alumni actions (such as reunions). Information can be imported from National Student Clearinghouse (http://www.studentclearinghouse.org/).
