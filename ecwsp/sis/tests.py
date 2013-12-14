from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group

from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *

from datetime import date, datetime

class AttendanceTest(TestCase):
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
<<<<<<< HEAD
        
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
=======
        self.teacher = Faculty(username="dburke", first_name="david", last_name="burke", teacher=True)
        self.teacher.save()
        if User.objects.filter(username="dburke").count() == 0:
            self.user = User.objects.create_user('dburke', 'ffdfsf@ffdsfsdf.com', 'aa')
        else:
            self.user = User.objects.get(username="dburke")
        self.user.is_staff = True
        self.user.save()
>>>>>>> 749bf05af37d4708060828f4fd0441bc858bc338
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
        
    def test_attendance(self):
        """
        Tests two teachers entering attendance, then admin changing it. Tests conflict resolution
        """
        self.setup()
        attend = StudentAttendance(student=self.student, date=date.today(), status=self.absent)
        attend.save()
        attend2 = StudentAttendance(student=self.student, date=date.today(), status=self.present)    # not a valid one! Should assume absent
        attend2.save()
        # admin changes it
        attend3, created = StudentAttendance.objects.get_or_create(student=self.student, date=date.today())
        
        # Verify absent
        self.failUnlessEqual(attend3.status, self.absent)
        
        attend3.status = self.excused
        attend3.notes = "Doctor"
        attend3.save()
        
        # Verify Excused
        self.failUnlessEqual(attend3.status, self.excused)
        
        # Verify no duplicates
        self.failUnlessEqual(StudentAttendance.objects.filter(date=date.today(), student=self.student).count(), 1)
    
    def test_teacher_attendance(self):
        self.setup()
        
        user = User.objects.get(username='dburke')
        user.set_password('aa') # Why is this needed?
        user.save()
        
        c = Client()
        
        c.login(username='dburke', password='aa')
        
        response = c.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        course = Course.objects.get(fullname="Homeroom FX 2010")
        
        response = c.get('/attendance/teacher_attendance/' + str(course.id), follow=True)
        self.assertEqual(response.status_code, 200)
        
        #should test if attendance can be submitted
    
    def test_grade(self):
        """
        Tests grade calculations
        """
        #testing that GPA actually calculates
        self.setup()
        
        courseneroll = CourseEnrollment(
            user=self.student,
            course=self.course2,
            role="student",
        )
        courseneroll.save()
        
        grade = Grade(
                student=self.student,
                course=self.course2,
                marking_period=self.mp,
            )
        grade.set_grade('50')
        grade.save()
        grade = Grade(
                student=self.student,
                course=self.course2,
                marking_period=self.mp2,
            )
        grade.set_grade('89.09')
        grade.save()
        print CourseEnrollment.objects.get(id=courseneroll.id).cache_grade 
        self.failUnlessEqual(self.student.gpa, Decimal('69.55'))

