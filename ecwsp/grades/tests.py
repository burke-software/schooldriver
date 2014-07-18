from ecwsp.sis.models import *
from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from models import *
from ecwsp.sis.sample_data import SisData
from django.db import connection
from ecwsp.schedule.models import CourseEnrollment, Course
import datetime

import time
import unittest


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
            CourseEnrollment(user=self.student, course_section=course_sections[0], role='student', grade=grades[0]),
            CourseEnrollment(user=self.student, course_section=course_sections[1], role='student', grade=grades[1]),
            CourseEnrollment(user=self.student, course_section=course_sections[2], role='student', grade=grades[2])
        ]
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
        self.build_grade_cache()

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
            [mp2, 2, 'B-'],
            [mp2, 3, 'D'],
            [mp2, 4, 'B'],
            [mp2, 5, 'D'],
            [mp2, 6, 'A'],
            [mp2, 7, 'B'],
            [mp2, 8, 'A'],
            [mp3, 1, 'F'],
            [mp3, 2, 'C'],
            [mp3, 3, 'C'],
            [mp3, 4, 'C'],
            [mp3, 5, 'C'],
            [mp3, 6, 'B'],
            [mp3, 7, 'C+'],
            [mp3, 8, 'A'],
            [mp4, 1, 'C'],
            [mp4, 2, 'C+'],
            [mp4, 3, 'D'],
            [mp4, 4, 'B+'],
            [mp4, 5, 'B'],
            [mp4, 6, 'A-'],
            [mp4, 7, 'B+'],
            [mp4, 8, 'A'],
        ]
        for x in test_data:
            grade = Grade.objects.get(marking_period=x[0], course_section_id=x[1])
            self.assertEqual(grade.get_grade(letter=True), x[2])

    def test_snx_grade(self):
        """ Really just a normal run of the mill Marking Period grade
        Balt uses s1x, s2x as tests that affect final grades
        """
        grade = Grade.objects.get(marking_period=self.data.mps1x, course_section_id=1)
        self.assertEqual(grade.get_grade(), 90)
        grade = Grade.objects.get(marking_period=self.data.mps2x, course_section_id=1)
        self.assertEqual(grade.get_grade(), 79)

    def test_partial_course_average_grade(self):
        """ Tests getting the average of some but not all marking period averages """
        s1_ids = [1,2,3]
        s2_ids = [4,5,6]
        test_data = [
            [1, s1_ids, 78.08, 'C+'],
            [1, s2_ids, 71.96, 'D'],
            [2, s1_ids, 68.16, 'F'],
            [2, s2_ids, 70.84, 'D'],
            [3, s1_ids, 68.0, 'F'],
            [3, s2_ids, 69.84, 'D'],
            [4, s1_ids, 87.52, 'B+'],
            [4, s2_ids, 80.88, 'B-'],
            [5, s1_ids, 73.6, 'C'],
            [5, s2_ids, 80.08, 'B-'],
            [6, s1_ids, 93.2, 'A'],
            [6, s2_ids, 86.65, 'B+'],
            [7, s1_ids, 79.04, 'C+'],
            [7, s2_ids, 83.12, 'B'],
            [8, s1_ids, 100, 'A'],
            [8, s2_ids, 100, 'A'],
        ]
        for x in test_data:
            ce = CourseEnrollment.objects.get(user=self.data.student, course_section=x[0])
            self.assertAlmostEqual(ce.get_average_for_marking_periods(x[1]), x[2])
            self.assertEqual(ce.get_average_for_marking_periods(x[1], letter=True), x[3])

    def test_scaled_average(self):
        """ Tests an asinine method for averages by converting to non linear scale first """
        test_data = [
            [1, Decimal(2.0)],
            [2, Decimal(2.4)],
            [4, Decimal(1.9)],
            [5, Decimal(2.8)],
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.student, marking_period=x[0])
            self.assertAlmostEqual(smpg.get_scaled_average(rounding=1), x[1])

    def test_average(self):
        test_data = [
            [3, 72.7],
            [6, 71.8],
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.student, marking_period=x[0])
            self.assertAlmostEqual(smpg.get_average(rounding=1), Decimal(x[1]))

    def test_scaled_multiple_mp_average(self):
        test_data = [
            [[1, 2, 3], Decimal(1.9)],
            [[4, 5, 6], Decimal(2.1)],
        ]
        for x in test_data:
            average = Grade.get_scaled_multiple_mp_average(self.data.student, x[0], rounding=1)
            self.assertAlmostEqual(average, x[1])

    def test_scaled_final_year_average(self):
        test_data = [
            [1, Decimal(2.2)],
        ]
        for x in test_data:
            year_grade = self.data.student.studentyeargrade_set.get(year=x[0])
            average = year_grade.get_grade(numeric_scale=True, rounding=1)
            self.assertAlmostEqual(average, x[1])

    def test_balt_gpa(self):
        gpa = self.data.student.get_gpa(rounding=1, numeric_scale=True)
        self.assertAlmostEqual(gpa, Decimal(2.2))

    def test_final_grade(self):
        test_data = [
            [1, 'C'],
            [2, 'D'],
            [3, 'D'],
            [4, 'B'],
            [5, 'C+'],
            [6, 'A-'],
            [7, 'B-'],
            [8, 'A'],
        ]
        for x in test_data:
            ce = CourseEnrollment.objects.get(user=self.data.student, course_section=x[0])
            with self.assertNumQueries(1):
                self.assertEqual(ce.get_grade(letter=True), x[1])

    def test_honors_and_ap_grades(self):
        """
        assert that the honors and ap grades receive correct boost by 
        replicating the grades in our manual spreadsheet
        """

        # Let's first make sure all the courses are of the correct type
        self.data.create_sample_honors_and_ap_data()

        # Now, test that the scaled averages are correct
        test_data = [
            {'mp_id': 1, 'scaled': Decimal(4.0), 'unscaled': Decimal(3.7)},
            {'mp_id': 2, 'scaled': Decimal(3.6), 'unscaled': Decimal(3.3)},
            {'mp_id': 4, 'scaled': Decimal(3.7), 'unscaled': Decimal(3.4)},
            {'mp_id': 5, 'scaled': Decimal(3.5), 'unscaled': Decimal(3.2)}
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.honors_student, marking_period=x['mp_id'])
            self.assertAlmostEqual(smpg.get_scaled_average(rounding=1), x['scaled'])


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
