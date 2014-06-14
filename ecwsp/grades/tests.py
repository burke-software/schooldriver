from ecwsp.sis.models import *
from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from models import *
from ecwsp.sis.sample_data import SisData
from django.db import connection
from ecwsp.schedule.models import CourseEnrollment
import datetime


class GradeCalculationTests(SisTestMixin, TestCase):
    def old________setUp(self):
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

class GradeBaltTests(SisTestMixin, TestCase):
    """ These test ensure we meet requirements defined by Cristo Rey Baltimore including
    Grade scales, course weights, and letter grades
    Sample data is anonomized real grade data """
    def populate_database(self):
        """ Override, not using traditional test data """
        self.data = SisData()
        self.data.create_grade_scale_data()
    
    def test_letter_grade(self):
        mp1 = self.data.mp1
        mp2 = self.data.mp2
        mp3 = self.data.mp3
        mp4 = self.data.mp4
        test_data = [
            [mp1, 1, 'C'],
            [mp1, 2, 'F'],
            [mp1, 3, 'F'],
            [mp1, 4, 'A-'],
            [mp1, 5, 'B-'],
            [mp1, 6, 'A'],
            [mp1, 7, 'B-'],
            [mp1, 8, 'A'],
            [mp2, 1, 'C+'],
        ]
        for x in test_data:
            grade = Grade.objects.get(marking_period=x[0], course_section_id=x[1])
            self.assertEqual(grade.get_grade(letter=True), x[2])
    

class GradeScaleTests(SisTestMixin, TestCase):
    def setUp(self):
        super(GradeScaleTests, self).setUp()
        self.build_grade_cache() 
        scale = self.scale = GradeScale.objects.create(name="test")
        GradeScaleRule.objects.create(min_grade=50, max_grade=59.99, letter_grade='F', numeric_scale=1, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=60, max_grade=69.99, letter_grade='D', numeric_scale=1.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=70, max_grade=79.99, letter_grade='C', numeric_scale=2, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=80, max_grade=89.99, letter_grade='B', numeric_scale=3, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=90, max_grade=90, letter_grade='A', numeric_scale=4, grade_scale=scale)
        self.data.school_year.grade_scale = scale
        self.data.school_year.save()

    def test_grade_scale(self):
        scale = self.scale
        self.assertEqual(scale.to_letter(50), 'F')
        self.assertEqual(scale.to_letter(59.99), 'F')
        self.assertEqual(scale.to_letter(55.34234), 'F')
        self.assertEqual(scale.to_letter(1000), None)
        self.assertEqual(scale.to_numeric(50), 1)

        # Now for some student grades
        student = self.data.student
        self.assertEqual(scale.to_letter(student.gpa), 'D')  # 69.55

        grade = self.data.grade
        self.assertEqual(grade.get_grade(letter=True), 'F')  # 50

    def test_scale_lookup_speed(self):
        import time
        grade = self.data.grade
        start = time.time()
        i = 1000
        for _ in range(i):
            grade.get_grade(letter=True)
        end = time.time()
        run_time = end - start
        print '{} scale lookups took {} seconds'.format(i, run_time)
        with self.assertNumQueries(1):
            grade.get_grade(letter=True)
