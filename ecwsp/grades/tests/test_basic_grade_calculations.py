from ecwsp.grades.models import Grade
from ecwsp.sis.models import Student, SchoolYear
from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from ecwsp.sis.sample_data import SisData
from ecwsp.schedule.models import (
    CourseEnrollment, Course, CourseSection, MarkingPeriod
    )
import datetime

class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.build_grade_cache()

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
        section = self.data.course_section1
        enroll = self.data.course_enrollment
        grade1, created = Grade.objects.get_or_create(
            student=student,
            course_section=section,
            marking_period=mp1,
            grade=mark1,)
        grade2, created = Grade.objects.get_or_create(
            student=student,
            course_section=section,
            marking_period=mp2,
            grade=mark2,)
        self.assertEquals(
            enroll.get_grade(date_report=datetime.date(2099, 1, 1)),
            75)
        self.assertEquals(
            enroll.get_grade(date_report=datetime.date(2014, 10, 1)),
            50)

    # Test compares two ways of calling calculate_grade()
    # There shouldn't be a discrepancy
    def test_current_vs_older(self):
        self.student = Student(first_name='Billy', last_name='Bob', username='BillyB', id=12345)
        self.student.save()
        self.year = SchoolYear(name='2011-2012', start_date='2011-09-10', end_date='2012-06-15', grad_date='2012-06-17',
                               id=2011)
        self.year.save()
        self.mp = MarkingPeriod(name="tri1 2011", start_date='2011-09-10', end_date='2012-06-15', school_year=self.year, monday=True, friday=True)
        self.mp.save()
        self.mp2 = MarkingPeriod(name="tri2 2012", start_date='2011-09-10', end_date='2012-06-15', school_year=self.year, monday=True, friday=True)
        self.mp2.save()
        self.mp3 = MarkingPeriod(name="tri3 2012", start_date='2011-09-10', end_date='2012-06-15', school_year=self.year, monday=True, friday=True)
        self.mp3.save()
        courses = [Course(fullname='Algebra', shortname='alg', id=12, credits=4),
                   Course(fullname='English', shortname='eng', id=13, credits=4),
                   Course(fullname='History', shortname='hist', id=14, credits=4)]
        course_sections = []
        for course in courses:
            course.save()
            course_section = CourseSection(
                course=course,
                name=course.fullname
            )
            course_section.save()
            course_sections.append(course_section)
        course_sections[0].marking_period.add(self.mp)
        course_sections[1].marking_period.add(self.mp2)
        course_sections[2].marking_period.add(self.mp3)
        grades = [
            Grade(
                student=self.student,
                course_section=course_sections[0],
                grade=86.78,
                marking_period=self.mp
            ), Grade(
                student=self.student,
                course_section=course_sections[1],
                grade=94.73,
                marking_period=self.mp2
            ), Grade(
                student=self.student,
                course_section=course_sections[2],
                grade=77.55,
                marking_period=self.mp3
            )
        ]
        for grade in grades:
            grade.save()
        course_enrollments = [
            CourseEnrollment(user=self.student, course_section=course_sections[0], grade=grades[0]),
            CourseEnrollment(user=self.student, course_section=course_sections[1], grade=grades[1]),
            CourseEnrollment(user=self.student, course_section=course_sections[2], grade=grades[2])
        ]
        for course_enrollment in course_enrollments:
            course_enrollment.save()
        StudentYearGrade.objects.create(student=self.student, year=self.year)
        syg = self.student.studentyeargrade_set.get(year=self.year)
        current = syg.calculate_grade_and_credits(date_report=datetime.date.today())
        older = syg.calculate_grade_and_credits()
        self.assertEqual(current, older)

