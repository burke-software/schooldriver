from ecwsp.grades.models import Grade
from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from ecwsp.sis.sample_data import SisData
from ecwsp.schedule.models import CourseEnrollment
from ..models import FinalGrade
import datetime


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()

    def get_simple_test_data(self):
        student = self.data.student
        mp1 = self.data.marking_period
        mp2 = self.data.marking_period2
        mp3 = self.data.marking_period3
        course = self.data.course_section1
        return [
            [student, course, mp1, 100, 100],
            [student, course, mp2, 50, 75],
            [student, course, mp3, 90.5, 80.17],
        ]

    def set_grade(self, enrollment, mp, grade):
        grade_obj = Grade(enrollment=enrollment, marking_period=mp)
        grade_obj.set_grade(grade)
        grade_obj.save()

    def set_final_grade(self, enrollment, grade):
        grade_obj = FinalGrade(enrollment=enrollment)
        grade_obj.set_grade(grade)
        grade_obj.save()

    def check_grade(self, enrollment, expect, date=None):
        average = Grade.get_course_grade(enrollment, date=date)
        self.assertEquals(average, expect)

    def set_and_check_grade(self, enrollment, mp, grade, expect,
                            date=None):
        self.set_grade(enrollment, mp, grade)
        self.check_grade(enrollment, expect, date=date)

    def test_basic_grades(self):
        """ /docs/specs/course_grades.md#Rounding """
        for data in self.get_simple_test_data():
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_and_check_grade(enrollment, data[2], data[3], data[4])

    def test_course_average_respect_time(self):
        """ See /docs/specs/course_grades.md#Time and averages
        mp1 start_date=`2014-07-1` and end_date=`2014-9-1`
        mp2 start_date=`2014-9-2` and end_date=`2015-3-1`
        """
        mark1 = 50
        mark2 = 100
        student = self.data.student
        mp1 = self.data.marking_period
        mp2 = self.data.marking_period2
        date1 = datetime.date(2099, 1, 1)
        date2 = datetime.date(2014, 10, 1)
        section = self.data.course_section1
        enroll = self.data.course_enrollment
        self.set_grade(enroll, mp1, mark1)
        self.set_grade(enroll, mp2, mark2)
        self.check_grade(enroll, 75, date=date1)
        self.check_grade(enroll, 50, date=date2)

    def test_marking_period_weight(self):
        """ See /docs/specs/course_grades.md#Marking Period Weights """
        mp1 = self.data.marking_period
        mp1.weight = 1.5
        mp1.save()
        test_data = self.get_simple_test_data()
        # Adjust expected for mp1 weight of 1.5
        test_data[1][4] = 80
        test_data[2][4] = 83
        for data in test_data:
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_and_check_grade(enrollment, data[2], data[3], data[4])

    def test_final_override(self):
        """ See /docs/specs/course_grades.md#Marking Period Weights """
        test_data = self.get_simple_test_data()
        for data in test_data:
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_grade(enrollment, data[2], data[3])
        self.set_final_grade(enrollment, 82)
        self.check_grade(enrollment, 82)
