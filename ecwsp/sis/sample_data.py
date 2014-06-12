# never import * except test data (because who cares about clean tests)
from ecwsp.sis.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *
from ecwsp.schedule.models import *


class SisData(object):
    """ Put data creation code here. sample data code not here is punishible by death .
    """
    def create_all(self):
        """ This will populate all sample data """
        self.create_basics()

    def stupid_hacks(self):
        """ Gross stuff goes here, this ideally delete this all """
        # No clue why this is needed. Won't get created in test env
        try:
            sql = '''CREATE TABLE `sis_studentcohort` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `student_id` integer NOT NULL,
                `cohort_id` integer NOT NULL,
                `primary` bool NOT NULL);'''
            cursor = connection.cursor()
            cursor.execute(sql)
        except:
            pass

    def create_required(self):
        """ A place for 100% required data """
        self.stupid_hacks()

    def create_basics(self):
        """ A very simple school, probably want this in mosts tests
        Depends on create_required
        """
        # Run dependencies first
        self.create_required()

        # Use bulk create a few so it looks good in demo
        SchoolYear.objects.bulk_create([
            SchoolYear(name="2013-2014", start_date=date(2013,7,1), end_date=date(2014,5,1)),
            SchoolYear(name="2014-long time", start_date=date(2014,7,1), end_date=date(2050,5,1), active_year=True),
            SchoolYear(name="2015-16", start_date=date(2015,7,1), end_date=date(2016,5,1)),
        ])
        # Set one archetypal object. If I want a year I will use this
        self.school_year = SchoolYear.objects.get(active_year=True)

        # Note bulk does not call save() and other limitations
        # so it's ok to not use bulk
        # Don't change the order, other objects depend on the id being in this order
        self.student = Student.objects.create(first_name="Joe", last_name="Student", username="jstudent")
        Student.objects.create(first_name="Jane", last_name="Student", username="jastudent")
        Student.objects.create(first_name="Tim", last_name="Duck", username="tduck")
        Student.objects.create(first_name="Molly", last_name="Maltov", username="mmaltov")

        MarkingPeriod.objects.bulk_create([
            MarkingPeriod(name="tri1 2014", start_date=date(2014,7,1), end_date=date(2014,9,1), school_year_id=2, monday=True, friday=True),
            MarkingPeriod(name="tri2 2014", start_date=date(2014,9,2), end_date=date(2015,3,1), school_year_id=2, monday=True, friday=True),
            MarkingPeriod(name="tri3 2014", start_date=date(2015,3,2), end_date=date(2050,5,1), school_year_id=2, monday=True, friday=True),
        ])
        self.marking_period = MarkingPeriod.objects.get(pk=1)

        self.teacher1 = self.faculty = Faculty.objects.create(username="dburke", first_name="david", last_name="burke", teacher=True)
        self.teacher2 = Faculty.objects.create(username="jbayes", first_name="jeff", last_name="bayes", teacher=True)
        aa = Faculty.objects.create(username="aa", first_name="aa", is_superuser=True, is_staff=True)
        aa.set_password('aa')
        aa.save()
        admin = Faculty.objects.create(username="admin", first_name="admin", is_superuser=True, is_staff=True)
        admin.set_password('admin')
        admin.save()

        Course.objects.bulk_create([
            Course(fullname="Math 101", shortname="Math101", credits=3, graded=True),
            Course(fullname="History 101", shortname="Hist101", credits=3, graded=True),
            Course(fullname="Homeroom FX 2011", shortname="FX1", homeroom=True, credits=1),
            Course(fullname="Homeroom FX 2012", shortname="FX2", homeroom=True, credits=1),
        ])
        self.course = Course.objects.get(id=1)

        CourseSection.objects.bulk_create([
            CourseSection(course_id=1, name="Math A"),
            CourseSection(course_id=1, name="Math B"),
            CourseSection(course_id=2, name="History A"),
            CourseSection(course_id=2, name="History A"),
        ])
        self.course_section = CourseSection.objects.get(pk=1)

        Period.objects.bulk_create([
            Period(name="Homeroom (M)", start_time=datetime.time(8), end_time=datetime.time(8, 50)),
            Period(name="First Period", start_time=datetime.time(9), end_time=datetime.time(9, 50)),
            Period(name="Second Period", start_time=datetime.time(10), end_time=datetime.time(10, 50)),
        ])
        self.period = Period.objects.get(id=1)

        CourseMeet.objects.bulk_create([
            CourseMeet(course_section_id=1, period=self.period, day="1"),
            CourseMeet(course_section_id=3, period=self.period, day="2"),
        ])

        self.course_section1 = CourseSection.objects.get(id=1)
        self.course_section2 = CourseSection.objects.get(id=2)
        self.course_section1.marking_period.add(1)
        self.course_section1.marking_period.add(2)
        self.course_section1.marking_period.add(3)
        self.course_section2.marking_period.add(1)
        self.course_section2.marking_period.add(2)
        self.course_section2.marking_period.add(3)

        self.enroll1 = CourseSectionTeacher.objects.create(course_section_id=1, teacher=self.teacher1)
        self.enroll2 = CourseSectionTeacher.objects.create(course_section_id=3, teacher=self.teacher2)
        self.present = AttendanceStatus.objects.create(name="Present", code="P", teacher_selectable=True)
        self.absent = AttendanceStatus.objects.create(name="Absent", code="A", teacher_selectable=True, absent=True)
        self.excused = AttendanceStatus.objects.create(name="Absent Excused", code="AX", absent=True, excused=True)

        CourseEnrollment.objects.bulk_create([
            CourseEnrollment(user=self.student, course_section_id=1),
            CourseEnrollment(user=self.student, course_section_id=2),
        ])
        self.course_enrollment = CourseEnrollment.objects.get(pk=1)

        Grade.objects.bulk_create([
            Grade(student_id=1, course_section_id=2, marking_period_id=1, grade=50),
            Grade(student_id=1, course_section_id=2, marking_period_id=2, grade=89.09)
        ])
        self.grade = Grade.objects.get(pk=1)

    def create_grade_scale_data(self):
        aa = Faculty.objects.create(username="aa", first_name="aa", is_superuser=True, is_staff=True)
        aa.set_password('aa')
        aa.save()
        student = Student.objects.create(first_name="Alexander", last_name="Chandel", username="achandel")
        courses = Course.objects.bulk_create([
            Course(fullname="English", shortname="English", credits=1, graded=True),
            Course(fullname="Precalculus", shortname="Precalc", credits=1, graded=True),
            Course(fullname="Physics", shortname="Phys", credits=1, graded=True),
            Course(fullname="Modern World History", shortname="Hist", credits=1, graded=True),
            Course(fullname="Spanish III", shortname="Span", credits=1, graded=True),
            Course(fullname="Photojournalism", shortname="Photo", credits=0, graded=True),
            Course(fullname="Faith & Justice", shortname="Faith", credits=1, graded=True),
            Course(fullname="Writing Lab 12", shortname="Wrt Lab", credits=0, graded=True),
        ])
        year = SchoolYear.objects.create(name="balt year", start_date=date(2014,7,1), end_date=date(2050,5,1), active_year=True)
        mp1 = MarkingPeriod.objects.create(name="1st", start_date=date(2014,7,1), end_date=date(2014,9,1), school_year=year)
        mp2 = MarkingPeriod.objects.create(name="2nd", start_date=date(2014,7,2), end_date=date(2014,9,2), school_year=year)
        mp3 = MarkingPeriod.objects.create(name="3rd", start_date=date(2014,7,3), end_date=date(2014,9,3), school_year=year)
        mp4 = MarkingPeriod.objects.create(name="4th", start_date=date(2014,7,4), end_date=date(2014,9,4), school_year=year)
        for course in courses:
            course = Course.objects.get(fullname=course.fullname)
            section = CourseSection.objects.create(name=course.shortname, course_id=course.id)
            section.marking_period.add(mp1)
            section.marking_period.add(mp2)
            section.marking_period.add(mp3)
            section.marking_period.add(mp4)
            CourseEnrollment.objects.create(user=student, course_section=section)
        grade_data = [
            [1, mp1, 72.7],
            [1, mp2, 77.5],
            [1, mp3, 66.5],
            [1, mp4, 73.9],
        ]
        for x in grade_data:
            grade = Grade.objects.get(student=student, course_section_id=x[0], marking_period=x[1])
            grade.grade = x[2]
            grade.save()
