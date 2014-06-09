from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group

from ecwsp.sis.models import *
from ecwsp.sis.sample_data import *
from ecwsp.schedule.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *

from datetime import date, datetime
from django.db import connection

class SisTestMixin(object):
    """ Making a test, use me please """
    def setUp(self):
        """ Prepares simple school data. """
        self.populate_database()

    def populate_database(self):
        """ Extend me with more data to populate """
        self.data = SisData()
        self.data.create_basics()
        

class AttendanceTest(SisTestMixin, TestCase):
    def test_attendance(self):
        """
        Tests two teachers entering attendance, then admin changing it. Tests conflict resolution
        """
        attend = StudentAttendance(student=self.data.student, date=date.today(), status=self.data.absent)
        attend.save()
        attend2 = StudentAttendance(student=self.data.student, date=date.today(), status=self.data.present)    # not a valid one! Should assume absent
        attend2.save()
        # admin changes it
        attend3, created = StudentAttendance.objects.get_or_create(student=self.data.student, date=date.today())
        
        # Verify absent
        self.failUnlessEqual(attend3.status, self.data.absent)
        
        attend3.status = self.data.excused
        attend3.notes = "Doctor"
        attend3.save()
        
        # Verify Excused
        self.failUnlessEqual(attend3.status, self.data.excused)
        
        # Verify no duplicates
        self.failUnlessEqual(StudentAttendance.objects.filter(date=date.today(), student=self.data.student).count(), 1)
    
    def test_teacher_attendance(self):
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
        
        #should test if attendance can be submitted
    
    def test_grade(self):
        """
        Testing that GPA actually calculates
        """
        from ecwsp.grades.tasks import build_grade_cache
        build_grade_cache()
        
        gpa = self.data.student.gpa.quantize(Decimal('0.01'))
        self.failUnlessEqual(gpa, Decimal('69.55'))
