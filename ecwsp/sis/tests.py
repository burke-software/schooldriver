from django.test import TestCase
from django.test import TransactionTestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group

from ecwsp.sis.models import *
from ecwsp.sis.sample_data import *
from ecwsp.schedule.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *

import datetime
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

    def build_grade_cache(self):
        from ecwsp.grades.tasks import build_grade_cache
        build_grade_cache()


class ReportTest(SisTestMixin, TestCase):
    def test_show_incomplete_without_grade(self):
        """ Test the setting TRANSCRIPT_SHOW_INCOMPLETE_COURSES_WITHOUT_GRADE
        """
        from constance import config
        import autocomplete_light
        autocomplete_light.autodiscover()
        from .scaffold_reports import SisReport

        sis_report = SisReport()
        student = self.data.student
        check_date = datetime.date(2013, 10, 10)
        sis_report.date_end = check_date
        sis_report.report_context['date_end'] = check_date
        sis_report.pass_letters = ''
        sis_report.get_student_transcript_data(student)
        self.assertTrue(student.years.count() == 0)

        config.TRANSCRIPT_SHOW_INCOMPLETE_COURSES_WITHOUT_GRADE = True
        sis_report.get_student_transcript_data(student)
        self.assertTrue(student.years.count() > 0)
        self.assertTrue(student.years[0].hide_grades)


class AttendanceTest(SisTestMixin, TestCase):
    def test_attendance(self):
        """
        Tests two teachers entering attendance, then admin changing it. Tests conflict resolution
        """
        attend = StudentAttendance(
            student=self.data.student, date=datetime.date.today(), status=self.data.absent)
        attend.save()
        attend2 = StudentAttendance(
            student=self.data.student, date=datetime.date.today(), status=self.data.present)    # not a valid one! Should assume absent
        attend2.save()
        # admin changes it
        attend3, created = StudentAttendance.objects.get_or_create(
            student=self.data.student, date=datetime.date.today())

        # Verify absent
        self.failUnlessEqual(attend3.status, self.data.absent)

        attend3.status = self.data.excused
        attend3.notes = "Doctor"
        attend3.save()

        # Verify Excused
        self.failUnlessEqual(attend3.status, self.data.excused)

        # Verify no duplicates
        self.failUnlessEqual(StudentAttendance.objects.filter(
            date=datetime.date.today(), student=self.data.student).count(), 1)

    def test_teacher_attendance(self):
        return
        user = User.objects.get(username='dburke')
        user.set_password('aa') # Why is this needed?
        user.save()

        c = Client()

        c.login(username='dburke', password='aa')

        response = c.get('/admin/')
        self.assertEqual(response.status_code, 200)

        course_section = CourseSection.objects.get(name="Homeroom FX 2011")

        response = c.get('/attendance/teacher_attendance/' + str(course_section.id), follow=True)
        self.assertEqual(response.status_code, 200)

        #should test if attendance can be submitted
