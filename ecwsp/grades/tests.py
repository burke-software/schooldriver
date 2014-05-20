from ecwsp.sis.models import *
from django.test import TestCase
from models import *
from django.db import connection
from ecwsp.schedule.models import CourseEnrollment
import datetime


class GradeCalculationTests(TestCase):
    def setUp(self):
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

    # Test compares two ways of calling calculate_grade()
    # There shouldn't be a discrepancy
    def test_current_vs_older(self):
        courses = [Course(fullname='Algebra', shortname='alg', id=12, credits=4),
                   Course(fullname='English', shortname='eng', id=13, credits=4),
                   Course(fullname='History', shortname='hist', id=14, credits=4)]
        for course in courses:
            course.save()
        courses[0].marking_period.add(self.mp)
        courses[1].marking_period.add(self.mp2)
        courses[2].marking_period.add(self.mp3)
        grades = [Grade(student=self.student, course=courses[0], grade=86.78, marking_period=self.mp), Grade(student=self.student,
                  course=courses[1], grade=94.73, marking_period=self.mp2), Grade(student=self.student, course=courses[2],
                  grade=77.55, marking_period=self.mp3)]
        for grade in grades:
            grade.save()
        course_enrollments = [CourseEnrollment(user=self.student, course=courses[0], role='student', grade=grades[0]),
                              CourseEnrollment(user=self.student, course=courses[1], role='student', grade=grades[1]),
                              CourseEnrollment(user=self.student, course=courses[2], role='student', grade=grades[2])]
        for course_enrollment in course_enrollments:
            course_enrollment.save()
        StudentYearGrade.objects.create(student=self.student, year=self.year)
        syg = self.student.studentyeargrade_set.get(year=self.year)
        current = syg.calculate_grade_and_credits(date_report=datetime.date.today())
        older = syg.calculate_grade_and_credits()
        self.assertEqual(current, older)

