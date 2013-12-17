from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group

from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *

from datetime import date, datetime

class ExampleTest(TestCase):
    def test_basic_addition(self):
        """ Tests that 1 + 1 always equals 2. """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class DashletTests(TestCase):
    def setup(self):
        """ Prepares simple school data. """
        
        self.student = Student(first_name="Joe", last_name="Student", username="jstudent")
        self.student.save()
        self.year = SchoolYear(name="2010-2011", start_date=date(2010,7,1), end_date=date(2011,5,1), active_year=True)
        self.year.save()
        self.mp = MarkingPeriod(name="tri1 2010", start_date=date(2010,7,1), end_date=date(2010,9,1), school_year=self.year, monday=True, friday=True)
        self.mp.save()
        self.mp2 = MarkingPeriod(name="tri2 2010", start_date=date(2010,9,2), end_date=date(2011,3,1), school_year=self.year, monday=True, friday=True)
        self.mp2.save()
        self.mp3 = MarkingPeriod(name="tri3 2010", start_date=date(2011,3,2), end_date=date(2050,5,1), school_year=self.year, monday=True, friday=True)
        self.mp3.save()
        
        self.teacher1 = Faculty(username="dburke", first_name="david", last_name="burke", teacher=True)
        self.teacher1.save()
        self.teacher2 = Faculty(username="jbayes", first_name="jeff", last_name="bayes", teacher=True)
        self.teacher2.save()
        try:
            self.user1 = User.objects.create_user('dburke', 'ffdfsf1@ffdsfsdf.com', 'aa1')
            self.user2 = User.objects.create_user('jbayes', 'ffdfsf2@ffdsfsdf.com', 'aa2')
        except:
            self.user1 = User.objects.get(username="dburke")
            self.user2 = User.objects.get(username="jbayes")
        self.user1.is_staff = True
        self.user2.is_staff = True
        self.user1.save()
        self.user2.save()
        group = Group.objects.get_or_create(name="teacher")[0]
        group.save()
        self.user1.groups.add(group)
        self.user2.groups.add(group)
        group2 = Group.objects.get_or_create(name="faculty")[0]
        group2.save()
        self.user1.groups.add(group2)
        self.user2.groups.add(group2)
        self.user1.save()
        self.user2.save()
        
        self.course1 = Course(fullname="Homeroom FX 2011", shortname="FX1", teacher=self.teacher1, homeroom=True, credits=1)
        self.course1.save()
        self.course2 = Course(fullname="Homeroom FX 2012", shortname="FX2", teacher=self.teacher2, homeroom=True, credits=1)
        self.course2.save()
        self.period = Period(name="Homeroom (M)", start_time=datetime.now(), end_time=datetime.now())
        self.period.save()
        self.course_meet1 = CourseMeet(course=self.course1, period=self.period, day="1")
        self.course_meet1.save()
        self.course_meet2 = CourseMeet(course=self.course2, period=self.period, day="2")
        self.course_meet2.save()
        self.course1.marking_period.add(self.mp)
        self.course1.marking_period.add(self.mp2)
        self.course1.marking_period.add(self.mp3)
        self.course1.save()
        self.course2.marking_period.add(self.mp)
        self.course2.marking_period.add(self.mp2)
        self.course2.marking_period.add(self.mp3)
        self.course2.save()
        
        self.enroll1 = CourseEnrollment(course=self.course1, user=self.teacher1)
        self.enroll1.save()
        self.enroll2 = CourseEnrollment(course=self.course2, user=self.teacher2)
        self.enroll2.save()
        self.present = AttendanceStatus(name="Present", code="P", teacher_selectable=True)
        self.present.save()
        self.absent = AttendanceStatus(name="Absent", code="A", teacher_selectable=True, absent=True)
        self.absent.save()
        self.excused = AttendanceStatus(name="Absent Excused", code="AX", absent=True, excused=True)
        self.excused.save()
        
    
    def test_teacher_attendance(self):
        """ Tests to ensure that we can take attendance. This test covers 
                the submission_percentage dashlet and teacher_submission view. """
        self.setup()
        
        user = User.objects.get(username='dburke')
        user.set_password('aa') # Why is this needed?
        user.save()
        
        c = Client()
        
        c.login(username='dburke', password='aa')
        
        response = c.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        course = Course.objects.get(fullname="Homeroom FX 2011")
        
        response = c.get('/attendance/teacher_attendance/' + str(course.id), follow=True)
        self.assertEqual(response.status_code, 200)
        
        AttendanceLog(user=user, course=self.course1).save()
        AttendanceLog(user=user, course=self.course2).save()
        
        homerooms = Course.objects.filter(homeroom=True)
        for homeroom in homerooms:
            log = AttendanceLog.objects.filter(course=homeroom)
            assert log.count() > 0
                
